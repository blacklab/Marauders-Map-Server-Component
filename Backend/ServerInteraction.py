#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from ServerSettings import *
import uuid

class ServerInteraction(object):

    listOFAllOther = None

    def __init__ (self, back):
        self.back = back
        self.listOfAllOther = None
        self.listofallinradius = []
        self.serverComponent = None

    def set_server_component(self, serverComponent):
        self.serverComponent = serverComponent
        
    #User Availability
    
    def set_user_available(self, jid):
        '''
        @type jid: str
        '''
        self.back.set_user_available(jid)
        
    def set_user_unavailable(self, jid):
        '''
        @type jid: str
        '''
        self.back.set_user_unavailable(jid)
    
    #User Settings    
    
    def update_settings(self, jID, settings):
        return self.back.update_settings(jID,settings)
    
    def get_settings(self, jID):
        return self.back.get_settings(jID)
    
    #User Info
    
    def get_user_info(self, callerjID, aboutjID):
        return self.back.get_user_info(callerjID, aboutjID)
    
    def get_jid_of_all_users(self):
        return self.back.get_jid_of_all_users()

    #User Avatar
    
    def save_avatar(self, ownerJID, avatarData):
        r = self.back.save_avatar(ownerJID, avatarData)
        
        if r == False:
            return
        
        #send buddysight out to all people around me
        peopleWhoSeeMySight = self.back.get_all_for_buddysight(ownerJID)
        
        for user in peopleWhoSeeMySight:
            print 'send avatar to ' , user['jid']
            self.serverComponent.sendAvatar(unicode(uuid.uuid4()),user['jid'], ownerJID, avatarData)

    def get_avatar_for_username(self, ownerName):
        return self.back.get_avatar_for_username(ownerName)

    def get_jid_from_username(self, username):
        return self.back.get_jid_from_username(username)
    
    #Friendships

    def create_friendship(self, callerJID, friendJID):
        '''
        Notify backend that callerJID and friendJID became friends on Jabber Server.
        
        This function is called by the user who accepts a friendship.
        
        NOT SAVE: anybody could establish a friendship. Should ask server!!!
        '''
        return self.back.create_friendship(callerJID, friendJID)
    
    def destroy_friendship(self, callerJID, lostFriendJID):
        '''
        Notify backend that callerJID and lostFriendJID are not friends on the JABEr Server no more.
        
        This function is called by the user who destroys the friendship
        
        NOT SAVE: any client could call this method without destroying the friendship onf the Jabber Server.
        '''
        return self.back.destroy_friendship(callerJID, lostFriendJID)

    #Geolocation related

    def refresh_geo_loc (self, jID, geodata):
        '''
        Refreshes the geolocation of the user with the given jid and will send the geolocation to all the users who are allowed
        to see him or her.
        
        @type back: MaraudersMapBackEnd
        '''
        try:
            if geodata.has_key('long') and geodata.has_key('lat') and geodata.has_key('accuracy'):
                self.back.refresh_geo_loc(jID, float(geodata['long']), float(geodata['lat']), float(geodata['accuracy']))
            
            # Hole die JIDs der Leute, die mich sehen duerfen.
            peopleWhoSeeMe = self.back.get_all_in_radius(jID)
            
            # sende an jeden meine GeoDaten
            for user in peopleWhoSeeMe:
                self.serverComponent.sendGeoLocMessage(user['relation'], user['jid'], jID, geodata)
            return True
        except:
            return False
    
    def share_geo_loc(self, senderJID, receiverUsername, geodata):
        '''
        Sends the shared geolocationt to the receiver
        '''
        
        #handle share like sending email...
        self.back.share_geo_loc(senderJID, receiverUsername, geodata)
        
        #send message to receiver
        receiver = receiverUsername + "@" + SERVER_DOMAIN
        self.serverComponent.sendShareGeoLocMessage(receiver, senderJID, geodata)