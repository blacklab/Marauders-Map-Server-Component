#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from wokkel.subprotocols import XMPPHandler

from Backend.ServerSettings import *
import uuid

NS_AVATAR_STORAGE = 'storage:client:avatar'
NS_IQ_AVATAR = 'jabber:iq:avatar'
NS_AVATAR_DATA = 'urn:xmpp:avatar:data'
NS_PUBSUB_EVENT = 'http://jabber.org/protocol/pubsub#event'

IQ_SET = '/iq[@type="set"]'
IQ_GET = '/iq[@type="get"]'
IQ_RESULT = '/iq[@type="result"]'
IQ_ERROR = '/iq[@type="error"]'

IQ_SET_AVATAR = IQ_SET + '/query[@xmlns="' + NS_AVATAR_STORAGE + '"]'
IQ_GET_AVATAR = IQ_GET + '/query[@xmlns="' + NS_AVATAR_STORAGE + '"]'
IQ_RESULT_AVATAR = IQ_RESULT + '/query[@xmlns="' + NS_IQ_AVATAR + '"]'

class AvatarResult(domish.Element):
    '''
    Forms an iq stanza for sending an avatar to a certain user
    '''
    
    def __init__(self, id, toJID, fromJID, avatarData):
        '''
        @param id: the id of the avatar request (if there was one)
        @param id: int
        
        @param toJID: the receiver of the avatar data
        @type toJID: jid as string
        
        @param fromJID: the sender of the avatar data
        @type fromJID: jid as string
        
        @param avatarData: the avatar
        @type avatarData: Base64 encoded png
        '''
        
        domish.Element.__init__(self, (None, 'message'))
        
        self['to'] = toJID
        self['from'] = fromJID
        
        event = self.addElement((NS_PUBSUB_EVENT, 'event'))
        items = event.addElement('items')
        items['node'] = NS_AVATAR_DATA
        item = items.addElement('item')
        item['id'] = unicode(id)
        data = item.addElement((NS_AVATAR_DATA,'data'))
        data.addContent("%s" % avatarData)
        

class IQBasedAvatar(XMPPHandler):
    '''
    This class is an implementation of the XEP-0008 protocol. See: http://xmpp.org/extensions/xep-0008.html
    
    Some changes have been made to the protocol.
    
    Only public XML storage is supported for storing and retrieving avatar data. The iqs must be send to backend component.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def connectionInitialized(self):
        '''
        Set the observers for packages
        '''
        self.xmlstream.addObserver(IQ_SET_AVATAR, self._onSetAvatar)
        self.xmlstream.addObserver(IQ_GET_AVATAR, self._onGetAvatar)
        
    def _onSetAvatar(self, iq):
        '''
        A user has send a set avatar iq to backend. See documentation.
        
        This function will get the jid of the calling user and the avatar data and will call a method to store the data.
        '''
        
        #get sender and receiver jid and compare them
        if iq.hasAttribute('from') == False:
            return
        
        fromJID = jid.JID(iq['from'])
        
        #get avatar data as Base64
        try:
            avatarData = str(iq.query.data)
        except:
            return
        
        #call save method
        self.saveAvatar(fromJID, avatarData)
       
    def _onGetAvatar(self, iq):
        '''
        A user has request the avatar of another user.
        '''        
        if iq.hasAttribute('from') == False:
            return
        if iq.hasAttribute('to') == False:
            return
        
        senderJID = jid.JID(iq["from"])
        receiverJID = jid.JID(iq["to"])
        
        #get avatar data
        avatarData = self.getAvatar(receiverJID.user)
        ownerJID = self.getJIDFromUsername(receiverJID.user)
        
        if avatarData == False or avatarData == None:
            return  
        
        if ownerJID == False or ownerJID == None:
            return
        
        #send avatar data
        return self.sendAvatar(iq["id"], senderJID.userhost(), ownerJID.userhost(), avatarData)
    
    def saveAvatar(self, ownerJID, avatarData):
        '''
        This method should be overwritten and save the avatar data for the user with the ownerJID
        
        @param ownerJID: the jid of the user which avatar should be saved
        @type ownerJID: twisted.words.protocols.jabber.jid
        
        @param avatarData: the avatar
        @type avatarData: the avata data is a Base64 encoded png
        '''
        
    def getAvatar(self, ownerName):
        '''
        This method is called to receive the avatar of the user with the name = ownerName.
        
        Should be overwritten.
        
        @param ownerName: the username of the user whose avatar should be return. This is not the whole jid.
        '''
        return False
    
    def getJIDFromUsername(self, username):
        '''
        Should be overwritten. Returns the whole jid for the user with given username.
        
        @rtype: twisted.words.protocols.jabber.jid
        '''
        return False
        
    def sendAvatar(self, requestID, receiverJID, ownerJID, avatarData):
        '''
        Send the Base64 encoded avatar data to the user with given jid
     
        @param requestID: the id of the avatar request
        @param requestID: int
 
        @param receiverJID: the jid of the user the avatar will be send to
        @type receiverJID: jid as string
        
        @param ownerJID: the jid of the users whose avatar will be send
        @param ownerJID: jid as string
        
        @param avatarData: the avatar
        @type avatarData: the avata data is a Base64 encoded png       
        '''
        
        try:
            avatarPackage = AvatarResult(requestID, receiverJID, ownerJID, avatarData)
            self.send(avatarPackage)
            return True
        except:
            return False     