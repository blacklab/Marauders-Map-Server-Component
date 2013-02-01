#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from wokkel.xmppim import MessageProtocol, AvailablePresence, PresenceClientProtocol
from XEP.locationquery import LocationQuery
from XEP.jabberrpc  import JabberRPC
from XEP.IQBasedAvatar import IQBasedAvatar

class MaraudersProtocol(LocationQuery, MessageProtocol, JabberRPC, IQBasedAvatar, PresenceClientProtocol):
    
    '''
    This is the main protocol implementation for the xmpp component. It is used in maraudersserver.tac.
    
    It supports some basic XMPP protocols and some slightly customized XEPs.
    '''
    
    # @type backend ServerInteraction
    backend= None
    
    def __init__(self, backend_interaction, component=False):
        '''
        @param backend_interaction: The handler for cumminicating with the logic of the backend.
        @type backend_interaction: ServerInteraction 
        '''
        #init XEPs
        MessageProtocol.__init__(self)
        LocationQuery.__init__(self)
        JabberRPC.__init__(self)
        IQBasedAvatar.__init__(self)
        PresenceClientProtocol.__init__(self)
        self.component = component
        
        #register rpc functions
        self.registerMethodCall('getSettings', self.onGetSettings)
        self.registerMethodCall('setSettings', self.onSetSettings)
        self.registerMethodCall('getUserInfo', self.onGetUserInfo)
        self.registerMethodCall('createFriendship', self.onCreateFriendship)
        self.registerMethodCall('destroyFriendship', self.onDestroyFriendship)
        
        #give the backend (ServerInteraction) a reference to this protocol handler
        self.backend = backend_interaction
        self.backend.set_server_component(self)

    #Connection related
    
    def connectionMade(self):
        # subscribe for presence notices from all users
        allUsers = self.backend.get_jid_of_all_users()
        for userJID in allUsers:
            self.subscribe(userJID)
            
    def connectionLost(self, reason):
        print "Disconnected!"
        
    def connectionInitialized(self):
        LocationQuery.connectionInitialized(self)
        JabberRPC.connectionInitialized(self)
        MessageProtocol.connectionInitialized(self)
        IQBasedAvatar.connectionInitialized(self)
        PresenceClientProtocol.connectionInitialized(self)
        
    #User availability
    
    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        self.backend.set_user_available(entity.userhost())
        
    def unavailableReceived(self, entity, statuses=None):
        self.backend.set_user_unavailable(entity.userhost())
        
    #User Info
    
    def onGetUserInfo(self, iq, jidAbout):
        '''
        This functions is called remotely with Jabber RPC to gather the profile infos about a user.
        
        @rtype: a dictionary with the infos
        '''
        
        sender = jid.JID(iq["from"])
        try:
            result = self.backend.get_user_info(sender.userhost(), jidAbout)
            
            return result
        except:
            return False
        
    #User Settings
    
    def onSetSettings(self, iq, settings):
        '''
        This function is called remotely with Jabber RPC to change the settings of a user.
        
        @param settings: The names and values of the settings which will be changed
        @type settings: Dictionary
        '''
        try:
            sender = jid.JID(iq["from"])            
            result = self.backend.update_settings(sender.userhost(), settings)
            return result
        except:
            return False
        
    def onGetSettings(self, iq):
        '''
        This function is called remotely with Jabber RPC.
        
        It returns a list of settings for a user. See getSettings Antwort.xml for description.
        '''      
        sender = jid.JID(iq["from"]) 
        settings = self.backend.get_settings(sender.userhost())
        return settings
    
    #Friendships
    
    def onCreateFriendship(self, iq, jidFriend):
        '''
        This function is called remotely with Jabber RPC
        
        It creates a friendship between the caller and the user with jidFriend.
        '''
        caller = jid.JID(iq["from"]) 
        r= self.backend.create_friendship(caller.userhost(), jidFriend)
        
        return r
    
    def onDestroyFriendship(self, iq, jidFriend):
        '''
        This function is called remotely with Jabber RPC
        
        It destroys a friendship between the caller and the user with jidFriend.
        '''        
        caller = jid.JID(iq["from"]) 
        r= self.backend.destroy_friendship(caller.userhost(), jidFriend)
        
        return r
    
    #Buddy Sight / Avatar
    
    def saveAvatar(self, ownerJID, avatarData):
        '''
        Overwriting the saveAvatar function of the IQBasedAvatar class. See XEP.IQBasedAvatar.saveAvatar
        '''
        try:
            self.backend.save_avatar(ownerJID.userhost(), avatarData)
        except:
            return
        
    def getAvatar(self, ownerName):
        '''
        Overwriting the getAvatar function of the IQBasedAvatar class. See XEP.IQBasedAvatar.getAvatar
        '''
        try:
            avatarData = self.backend.get_avatar_for_username(ownerName)
            return avatarData
        except:
            return False
    
    def getJIDFromUsername(self, username):
        '''
        Overwriting the getJIDFromUsername function of the IQBasedAvatar class. See XEP.IQBasedAvatar.getJIDFromUsername
        '''
        try:
            userJID = self.backend.get_jid_from_username(username)
            return userJID
        except:
            return False
            
    #For location exchange
    
    def onLocationQuery(self, senderJID, geodata, iq):
        '''
        Overwriting the onLocationQuery handler of XEP.LocationQuery class. See XEP.LocationQuery.onLocationQuery.
        '''
        try:
            self.backend.refresh_geo_loc(senderJID, geodata)
        except:
            return
        
    def onLocationShare(self, senderJID, receiverUsername, geodata, iq): 
        '''
        Overwriting the onLocationQuery handler of XEP.LocationQuery class. See XEP.LocationQuery.onLocationShare.
        '''
        try:
            self.backend.share_geo_loc(senderJID, receiverUsername, geodata)
        except:
            return