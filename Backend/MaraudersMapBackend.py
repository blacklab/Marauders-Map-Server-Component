#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from Logic import Logic
from ServerInteraction import ServerInteraction
from DataBaseInteraction import DataBaseInteraction
from Logic import Logic

class MaraudersMapBackEnd(object):
    """BackEndHauptklasse"""

    listOfAllOther = None

    def __init__(self):
        self.listOfAllOther = None
        # @type dbI DataBaseInteraction
        # @type sv ServerInteraction
        # @type log Logic
        self.dbI = DataBaseInteraction(self) #self wieder einfuegen!
        self.sv = ServerInteraction(self)
        self.log = Logic(self,self.dbI)
        
    #User Settings
        
    def update_settings(self, jID, settings):
        '''
        Updates the settings for user with given jID
        '''
        return self.log.update_settings(jID, settings)
    
    def get_settings(self, jID):
        '''
        Get a list of all settings for a user with given jID.
        '''
        return self.log.get_settings(jID)
    
    #User info
    
    def get_user_info(self, callerjID, aboutjID):
        '''
        Get a dictionary of the infos about a user with given jID, and connetions to the caller.
        '''
        return self.log.get_user_info(callerjID, aboutjID)
    
    def get_jid_of_all_users(self):
        '''
        Returns a list of all user
        
        @rtype: list with jid as JID
        '''
        return self.log.get_jid_of_all_users()
    
    #User Availability
    
    def set_user_available(self, jid):
        '''
        @type jid: str
        '''
        self.log.set_user_available(jid)
        
    def set_user_unavailable(self, jid):
        '''
        @type jid: str
        '''
        self.log.set_user_unavailable(jid)
    
    #User Avatar
    
    def save_avatar(self, ownerJID, avatarData):
        return self.dbI.update_user_avatar(ownerJID, avatarData)
    
    def get_avatar_for_username(self, ownerName):
        return self.log.get_avatar_for_username(ownerName)
    
    def get_jid_from_username(self, username):
        return self.log.get_jid_from_username(username)
    
    def get_all_for_buddysight(self, jID):
        '''
        Gets a list of all users who will receive the buddy sight of the user with given jID.
        @rtype: list
        '''
        try:
            listofall = self.log.get_all_for_buddysight(jID)
            return listofall
        except:
            return list()
        
    #Geolocation related

    def get_all_in_radius(self, jID):
        '''
        Gets a list of all users who are in a radius for the user with the given JID.
        Thus returns a list of the users who are allowed to see the user with the given JID
        '''
        try:
            listofallinradius = self.log.get_list_of_all_in_radius(jID)
            return listofallinradius
        except:
            return list()

    def refresh_geo_loc(self, jID, long, lat, acc):
        '''
        Updates the location for user with given jID
        '''
        try:
            self.dbI.refresh_geo_loc(jID, long, lat, acc)
        except:
            print "db Error/ refresh Geo"  
        return True
    
    def share_geo_loc(self, senderJID, receiverUsername, geodata):
        '''
        Send a location send by user with senderJID to user with recevierUsername
        '''
        self.log.share_geo_loc(senderJID, receiverUsername, geodata)
    
    #Friendhsips related
    
    def create_friendship(self, callerJID, friendJID):
        '''
        Establish a friendship between callerJID and friendJID on database of backende
        '''
        return self.log.create_friendship(callerJID, friendJID)
    
    def destroy_friendship(self, callerJID, lostFriendJID):
        '''
        Destroy a friendhsip between callerJID and lostFriendJID
        '''
        return self.log.destroy_friendship(callerJID, lostFriendJID)

 #   def request_geo_loc_pub(self, jID):
 #       self.sv.request_from_server_geo_loc_pub(jID)
 #       return True