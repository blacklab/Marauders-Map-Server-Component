#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

import uuid
from types import *
from twisted.words.xish import domish
from wokkel.subprotocols import IQHandlerMixin, XMPPHandler
from twisted.words.protocols.jabber import jid

NS_PUBSUB_EVENT = 'http://jabber.org/protocol/pubsub#event'
NS_GEOLOC = 'http://jabber.org/protocol/geoloc'
NS_GEOLOCSHARE = 'http://jabber.org/protocol/geolocshare'
NS_LOCATION_QUERY = 'urn:xmpp:locationquery:0'

IQ_GET = '/iq[@type="get"]'
IQ_SET = '/iq[@type="set"]'
IQ_LOCATION_QUERY = IQ_GET + '/locationquery[@xmlns="' + NS_LOCATION_QUERY + '"]'
IQ_LOCATION_SHARE = IQ_SET + '/locationquery[@xmlns="' + NS_LOCATION_QUERY + '"]'

class ShareGeoLocMessage(domish.Element):
    
    def __init__(self, toJID, fromJID, geodata):   
        domish.Element.__init__(self, (None, 'message'))
        self.recipientJID = toJID
        self.senderJID = fromJID
        self.geodata = geodata
        
        self._formMessage()
        
    def _formMessage(self):
        '''
        Create XML elements of a message. See http://xmpp.org/extensions/xep-0080.html#usecases-pubsub
        '''
        
        self['from'] = self.senderJID
        self['to'] = self.recipientJID

        event = self.addElement((NS_PUBSUB_EVENT, 'event'))
        
        items = event.addElement('items')
        items['node'] = NS_GEOLOCSHARE
        
        item = items.addElement('item')
        
        #set unique id
        item['id'] = "%d" % uuid.uuid4()
        #message.addUniqueId()
        
        geoloc = item.addElement((NS_GEOLOC, 'geoloc'))
        geoloc['xml:lang'] = 'en'
        
        #add geodata elements (should contain at least lat, lon and acc)
        if isinstance(self.geodata, DictType):
            for key, e in self.geodata.items():
                geoloc.addElement(key, content = "%s" % e)              
        
class GeoLocMessage(domish.Element):
    
    def __init__(self, relation, toJID, fromJID, geodata):   
        domish.Element.__init__(self, (None, 'message'))
        self.relation = relation
        self.recipientJID = toJID
        self.senderJID = fromJID
        self.geodata = geodata
        self._formMessage()
        
    def _formMessage(self):
        '''
        Create XML elements of a message. See http://xmpp.org/extensions/xep-0080.html#usecases-pubsub
        '''
        
        self['from'] = self.senderJID
        self['to'] = self.recipientJID

        event = self.addElement((NS_PUBSUB_EVENT, 'event'))
        
        items = event.addElement('items')
        items['node'] = NS_GEOLOC + '#' + self.relation
        
        item = items.addElement('item')
        
        #set unique id
        item['id'] = "%d" % uuid.uuid4()
        #message.addUniqueId()
        
        geoloc = item.addElement((NS_GEOLOC, 'geoloc'))
        geoloc['xml:lang'] = 'en'
        
        #add geodata elements (should contain at least lat, lon and acc)
        if isinstance(self.geodata, DictType):
            for key, e in self.geodata.items():
                geoloc.addElement(key, content = "%s" % e)    

class LocationQuery(XMPPHandler):
    '''
    Protocol implementation for XMPP Location Query
    
    The handler will listen to location querys. It does not respond yet as requested by XEP-0255.
    
    It just calls the onFunctions.
    
    This protocol is extended with a specification for sharing geolocations. See "geodaten versenden.txt" in Dokumentation
    '''
    
    #iqHandlers = {IQ_LOCATION_QUERY: '_onLocationQuery'}

    def __init__(self):
        '''
        Constructor
        '''

    def connectionInitialized(self):
        self.xmlstream.addObserver(IQ_LOCATION_QUERY, self._onLocationQuery)
        self.xmlstream.addObserver(IQ_LOCATION_SHARE, self._onLocationShare)

        
    def _onLocationShare(self, iq):
        '''
        Handles a share location query. Gets latitude and longitude from iq.
        
        @param iq: The request iq element as twisted.words.xish.domish.Element.
        
        Note: The receiver adress is username@back.maraudersserver.com
        '''
        
        if iq.handled == True:
            return
        
        try:
            sender = jid.JID(iq["from"])
            receiver = jid.JID(iq["to"])
            
            geodata = dict()
            for child in iq.locationquery.children:
                geodata[child.name] = unicode(child)
            
        except:
            return
        
        #call own callback   
        self.onLocationShare(sender.userhost(), receiver.user, geodata, iq) 
        
    def onLocationShare(self, senderJID, receiverUsername, geodata, iq): 
        '''
        Called when a share location query was received. Should be overwritten.
        
        @param senderJID: The jid of the sender of the position
        @param receiverUsername: The username of the jid of the receiver of the position
        @param geodata: A dict with the geodata.
        @param iq: The request iq element.
        '''
              

    def _onLocationQuery(self, iq):
        '''
        Handles location query. Gets latitude and longitude from iq.
        
        @param iq: The request iq element as twisted.words.xish.domish.Element.
        '''
        if iq.handled == True:
            return
        
        # do error response defined by protocol
        
        # should server respond as defined in XEP-0255?
        
        try:
            sender = jid.JID(iq["from"]) 
            
            geodata = dict()
            for child in iq.locationquery.children:
                geodata[child.name] = unicode(child)
                
        except: # the location query request has not all elements
            return
        
        # call own callback
        self.onLocationQuery(sender.userhost() ,geodata, iq)
        
    def onLocationQuery(self, senderJID, geodata, iq):    
        '''
        Called when a location query was received. Should be overwritten.
        
        @param senderJID: The jid of the sender of the position
        @param geodata: a dictionary with all elements form <geoloc>
        @param iq: The request iq element.
        '''     
        
    def sendShareGeoLocMessage(self, toJID, fromJID, geodata):
        '''
        Creates and sends a Share GeoLoc Message to user of toJID.
        
        @param toJID: The the JID of client which receives this message.
        @type toJID: C{unicode}
        @param fromJID: The JID of the client which sends this message
        @type fromJID: C{unicode}
        @param geodata: the data of the location
        @type geodata: dict
        '''  
        
        #send message
        try:
            self.send(ShareGeoLocMessage(toJID, fromJID, geodata))
        except:
            print "Could not send pubsub share location message"      
               
    def sendGeoLocMessage(self, relation, toJID, fromJID, geodata):
        '''
        Creates and sends a GeoLoc Message to user of toJID.
        
        @param relation: The relation between receiver (toJID) and sender (fromJID)
        @type relation: String. Should be 'friend', 'acquaintance' or 'foreigner'
        @param toJID: The the JID of client which receives this message.
        @type toJID: C{unicode}
        @param fromJID: The JID of the client which sends this message
        @type fromJID: C{unicode}
        @param geodata: dictionary of elements of geoloc. all are strings
        '''  
        
        # send message
        try:
            self.send(GeoLocMessage(relation, toJID, fromJID, geodata))
        except:
            print "Could not send pubsub location message"