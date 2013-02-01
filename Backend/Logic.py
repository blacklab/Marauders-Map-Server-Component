#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from ServerSettings import *
from Mailing import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import math
from twisted.words.protocols.jabber import jid

class Logic(object):
 
    def __init__(self, back, dbI):
        self.back = back
        self.dbI = dbI
        
        #Map for database functions to update settings
        self.updateSettingFunctions = dict()
            #visibility 
        self.updateSettingFunctions['friendradius'] = self.dbI.update_friends_radius
        self.updateSettingFunctions['acquaintanceradius'] = self.dbI.update_acquaintances_radius
        self.updateSettingFunctions['foreignerradius'] = self.dbI.update_foreigners_radius
            #user info
        self.updateSettingFunctions['first_name'] = self.dbI.update_user_first_name
        self.updateSettingFunctions['name'] = self.dbI.update_user_name
        self.updateSettingFunctions['email'] = self.dbI.update_user_email_address
        self.updateSettingFunctions['show_name_flag'] = self.dbI.update_user_show_name_flag
        self.updateSettingFunctions['show_email_flag'] = self.dbI.update_user_show_email_flag
            #notification
        self.updateSettingFunctions['send_mail_notifications'] = self.dbI.update_user_mail_notifications
            #buddysight
        self.updateSettingFunctions['share_buddysight_friends_flag'] = self.dbI.update_user_share_buddysight_friends_flag
        self.updateSettingFunctions['share_buddysight_acquaintances_flag'] = self.dbI.update_user_share_buddysight_acquaintances_flag
        self.updateSettingFunctions['share_buddysight_foreigners_flag'] = self.dbI.update_user_share_buddysight_foreigners_flag

    #User Settings

    def update_settings(self, jID, settings):
        '''
        Update users settings
        '''
        for key, value in settings.items():
            if key in self.updateSettingFunctions.keys():
                try:
                    if self.updateSettingFunctions[key](jID, value) == False:
                        return False
                except:
                    return False
            else:
                return False
        return True
    
    def get_settings(self, jID):
        '''
        Get all settings for a user with given jID from database.
        
        @rtype: A List of several dictionaries. See getSettings Antwort.xml for details
        '''
        
        #put settings in right form
        result = list()
        
        #add visibility category
        settings = self.dbI.get_settings(jID)
        if settings == False:
            return list() #empty list. No settings can be made
        
        vis = dict()
        vis['header'] = VISIBILITY_HEADER
        vis['description'] = VISIBILITY_DESCRIPTION
        vis['settingoptions'] = settingOpts = list()
        if 'friendradius' in settings.keys():
            friendradius = self._appendOptionTo(settingOpts, 'friendradius', VISIBLITY_FRIENDS_RADIUS, settings['friendradius']) 
            friendradius['max'] = MAX_RADIUS
            friendradius['min'] = MIN_RADIUS
        if 'acquaintanceradius' in settings.keys():
            acquaintanceradius = self._appendOptionTo(settingOpts, 'acquaintanceradius', VISIBILITY_ACQUAINTANCE_RADIUS, settings['acquaintanceradius']) 
            acquaintanceradius['max'] = MAX_RADIUS
            acquaintanceradius['min'] = MIN_RADIUS
        if 'foreignerradius' in settings.keys():
            foreignerradius = self._appendOptionTo(settingOpts, 'foreignerradius', VISIBILITY_FOREIGNER_RADIUS, settings['foreignerradius']) 
            foreignerradius['max'] = MAX_RADIUS
            foreignerradius['min'] = MIN_RADIUS          
            
        result.append(vis)
        
        #notification settings
        notificationSettings = dict()
        notificationSettings['header'] = NOTIFICATION_SETTINGS_HEADER
        notificationSettings['description'] = NOTIFICATION_SETTINGS_DESCRIPTION
        notificationSettings['settingoptions'] = notSettingOpts = list()      
        if 'send_mail_notifications' in settings.keys():
            self._appendOptionTo(notSettingOpts, 'send_mail_notifications', NOTIFICATION_SETTINGS_EMAIL_NOTIFICATIONS, bool(settings['send_mail_notifications']))
        
        result.append(notificationSettings)
        
        #add buddy sight settings
        buddysightSettings = dict()
        buddysightSettings['header'] = BUDDYSIGHT_SETTINGS_HEADER
        buddysightSettings['description'] = BUDDYSIGHT_SETTINGS_DESCRIPTION
        buddysightSettings['settingoptions'] = bsSettingOpts = list() 
        if 'share_buddysight_friends' in settings.keys():
            self._appendOptionTo(bsSettingOpts, 'share_buddysight_friends_flag', BUDDYSIGHT_SETTINGS_SHARE_FRIENDS, bool(settings['share_buddysight_friends']))
        if 'share_buddysight_acquaintances' in settings.keys():
            self._appendOptionTo(bsSettingOpts, 'share_buddysight_acquaintances_flag', BUDDYSIGHT_SETTINGS_SHARE_ACQUAINTANCES, bool(settings['share_buddysight_acquaintances']))
        if 'share_buddysight_foreigners' in settings.keys():
            self._appendOptionTo(bsSettingOpts, 'share_buddysight_foreigners_flag', BUDDYSIGHT_SETTINGS_SHARE_FOREIGNERS, bool(settings['share_buddysight_foreigners']))                    
        
        result.append(buddysightSettings)  
        
        #add profile view settings
        profileviewSettings = dict()
        profileviewSettings['header'] = PROFILE_VIEW_SETTINGS_HEADER
        profileviewSettings['description'] = PROFILE_VIEW_SETTINGS_DESCRIPTION
        profileviewSettings['settingoptions'] = accSettingOpts = list()
        if 'show_name' in settings.keys():
            self._appendOptionTo(accSettingOpts, 'show_name_flag', PROFILE_VIEW_SETTINGS_SHOW_NAME, bool(settings['show_name']))
        if 'show_email' in settings.keys():
            self._appendOptionTo(accSettingOpts, 'show_email_flag', PROFILE_VIEW_SETTINGS_SHOW_EMAIL, bool(settings['show_email']))                
            
        result.append(profileviewSettings)      
       
        #add profile info
        profileInfo = self.dbI.get_user_info(jID)
        if profileInfo == False:
            profileInfo = dict()
           
        profile = dict()
        profile['header'] = PROFILE_SETTINGS_HEADER
        profile['description'] = PROFILE_SETTINGS_DESCRIPTION
        profile['settingoptions']  = profileSettingsOpts = list()         
        if 'first_name' in profileInfo.keys():
            self._appendOptionTo(profileSettingsOpts, 'first_name', PROFILE_SETTINGS_FIRST_NAME, profileInfo['first_name']) 
        if 'name' in profileInfo.keys():
            self._appendOptionTo(profileSettingsOpts, 'name', PROFILE_SETTINGS_NAME, profileInfo['name']) 
        if 'email' in profileInfo.keys():
            self._appendOptionTo(profileSettingsOpts, 'email', PROFILE_SETTINGS_EMAIL_ADDRESS, profileInfo['email']) 
            
        result.append(profile)
        
        return result
    
    def _appendOptionTo(self, optionList, optionKey, optionName, optionValue):
        '''
        Small helper function. Forms a dictionary and appends it to optionList
        @type optionKey: string
        @type optionName: string
        @type optionValue: string, bool, float ot int  
        
        @rtype: the option dictionary 
        '''
        option = dict()
        option['optionkey'] = optionKey
        option['displayname'] = optionName
        option['currentvalue'] = optionValue
        optionList.append(option)    
        
        return option
        
    #User info
    
    def get_user_info(self, callerjID, aboutjID):
        '''
        Gets the infos about a user with given jID from database an returns a dictionary of them.
        now with Aquaintance info
        '''              
        userInfo = self.dbI.get_user_info_with_aquaintace_info(callerjID, aboutjID)
        if userInfo == False:
            return list()
        
        result = list()
        
        #get aboutJID settings
        aboutUserSettings = self.dbI.get_settings(aboutjID)
        if aboutUserSettings == False:
            return list()    
        
        # general informations
        generalInfo = dict()
        generalInfo['header'] = GENERAL_INFO_HEADER
        generalInfo['description'] = GENERAL_INFO_DESCRIPTION
        generalInfo['info']  = info = list()       
        
        if 'show_name' in aboutUserSettings.keys():
            if aboutUserSettings['show_name']:
                if 'first_name' in userInfo.keys():
                    first_name = dict()
                    first_name['displayname'] = GENERAL_INFO_FIRST_NAME
                    first_name['currentvalue'] = userInfo['first_name']
                    info.append(first_name) 
                if 'name' in userInfo.keys():
                    name = dict()
                    name['displayname'] = GENERAL_INFO_NAME
                    name['currentvalue'] = userInfo['name']
                    info.append(name)
        if 'show_email' in aboutUserSettings.keys():
            if aboutUserSettings['show_email'] == 1:
                if 'email' in userInfo.keys():
                    avatar = dict()
                    avatar['displayname'] = GENERAL_INFO_EMAIL
                    avatar['currentvalue'] = userInfo['email']
                    info.append(avatar)      
        if 'acquaintance_over_name' in userInfo.keys() and 'acquaintance_over_first_name' in userInfo.keys():
            acquaintance_over = dict()
            acquaintance_over['displayname'] = GENERAL_INFO_ACQUAINTANCE_OVER
            acquaintance_over['currentvalue'] = str(userInfo['acquaintance_over_first_name']) + " " + str(userInfo['acquaintance_over_name'])
            info.append(acquaintance_over)
            
        result.append(generalInfo)
        
        # some other info
        
        return result
    
    def get_jid_from_username(self, username):
        '''
        Gets the whole jid for a user with given username.
        
        @rtype: twisted.words.protocols.jabber.jid (!)
        '''
        userJID = jid.JID(username + "@" + SERVER_DOMAIN)
        return userJID
    
    def get_avatar_for_username(self, ownerName):
        '''
        Returns the base64 encoded avatar of the user with the given ownerName
        
        @param ownerName: the name of the user NOT the jid.
        '''
        #build jid
        ownerJID = ownerName + "@" + SERVER_DOMAIN
        avatar = self.dbI.get_avatar_for_username(ownerJID)
        if 'avatar' in avatar.keys():
            return avatar['avatar']
        return 'no avatar set'
    
    def get_all_for_buddysight(self, jID):
        '''
        Fetches a list of all users who will receive a buddy sight from user with given jID. Usually the list
        will include all friends and acquaintances in the users radius and foreigners in the radius.
        '''
        
        #get settings for user
        senderSettings = self.dbI.get_settings(jID)
        
        listofAllWhoGetBuddySight = list()
        
        #get radii of the user with the given jid
        userData = self.dbI.get_radii_and_geodata_for_user(jID)
        if userData == False:
            return
        
        #get list of friends of user
        if 'share_buddysight_friends' in senderSettings.keys():
            if senderSettings['share_buddysight_friends']:
                listOfFriends = self.dbI.get_all_friends_of(jID)
                if listOfFriends != False:
                    try:
                        for friend in listOfFriends:
                            if friend['online'] == 'TRUE':
                                listofAllWhoGetBuddySight.append({'jid': friend['jid'], 'relation': 'friend'})
                            else:
                                pass
                    except:
                        print "Could not fetch friends"
            
        #get list of friends of friends of user
        if 'share_buddysight_acquaintances' in senderSettings.keys():
            if senderSettings['share_buddysight_acquaintances']:
                listOfFriendsOfFriends = self.dbI.get_all_acquaintances_of(jID)
                if listOfFriendsOfFriends != False:        
                    try:
                        for fof in listOfFriendsOfFriends:
                            if fof['online'] == 'TRUE' and self.is_geo_position_in_circle(userData, userData['acquaintanceradius'], fof):
                                listofAllWhoGetBuddySight.append({'jid': fof['jid'], 'relation': 'acquaintance'})
                            else:
                                pass
                    except:
                            print "Could not fetch friends of friends"  
                    
        #get list of foreigners of user
        if 'share_buddysight_foreigners' in senderSettings.keys():   
            if senderSettings['share_buddysight_foreigners']:
                listOfForeigners = self.dbI.get_all_foreigners_of(jID)
                if listOfForeigners != False:        
                    try:
                        for foreigners in listOfForeigners:
                            if foreigners['online'] == 'TRUE' and self.is_geo_position_in_circle(userData, userData['foreignerradius'], foreigners):
                                listofAllWhoGetBuddySight.append({'jid': foreigners['jid'], 'relation': 'foreigner'})
                            else:
                                pass
                    except:
                            print "Could not fetch foreigners"
                    
        #set pending relation all foreigners and acquaintances who are pending friends
        listOfPendingFriends = self.dbI.get_all_friendship_pendings_to(jID)
        if listOfPendingFriends != False:
            try:
                for pendJID in listofAllWhoGetBuddySight:
                    if pendJID['relation'] != 'friend' and self.is_listOfPendingFriends(pendJID['jid'], listOfPendingFriends):
                        pendJID['relation'] = 'pending'
            except:
                print "Could not set penders"

        return listofAllWhoGetBuddySight      
    
    def get_jid_of_all_users(self):
        '''
        Gets all registered users from db and returns a list of JIDs
        
        @rtype: list of twisted.words.protocols.jabber.jid (!)
        '''
        
        allUsers = self.dbI.get_jid_of_all_users()
        returnList = list()
        
        try:
            for userJID in allUsers:
                returnList.append(jid.JID(userJID['jid']))
        except:
            return list() #return an empty list on error          
        return returnList
    
    #User Availability
    
    def set_user_available(self, userJID):
        '''
        @type jid: str
        '''
        return self.dbI.update_user_availability(userJID, 'TRUE')
        
    def set_user_unavailable(self, userJID):
        '''
        @type jid: str
        '''
        return self.dbI.update_user_availability(userJID, 'FALSE')

    #Geolocation related
    

    def get_list_of_all_in_radius(self, jID):
        '''
        Returns a list of the users who are in a visibility radius for the user with the given jid 
        and are thus allowed to see him.
        
        There are three kinds of users: friends, friends of friends and foreigners.
        
        For now only the radius for foreigners is tested
        '''        
        listofAllWhoCanSee = list()
        
        #get radii of the user with the given jid
        userData = self.dbI.get_radii_and_geodata_for_user(jID)
        if userData == False:
            return
        
        #get list of friends of user
        listOfFriends = self.dbI.get_all_friends_of(jID)
        if listOfFriends != False:
            try:
                for friend in listOfFriends:
                    if friend['online'] == 'TRUE' and self.is_geo_position_in_circle(userData, userData['friendradius'], friend):
                        listofAllWhoCanSee.append({'jid': friend['jid'], 'relation': 'friend'})
                    else:
                        pass
            except:
                print "Could not fetch friends"
            
        #get list of friends of friends of user
        listOfFriendsOfFriends = self.dbI.get_all_acquaintances_of(jID)
        if listOfFriendsOfFriends != False:        
            try:
                for fof in listOfFriendsOfFriends:
                    if fof['online'] == 'TRUE' and self.is_geo_position_in_circle(userData, userData['acquaintanceradius'], fof):
                        listofAllWhoCanSee.append({'jid': fof['jid'], 'relation': 'acquaintance'})
                    else:
                        pass
            except:
                    print "Could not fetch friends of friends"  
                    
        #get list of foreigners of user   
        listOfForeigners = self.dbI.get_all_foreigners_of(jID)
        if listOfForeigners != False:        
            try:
                for foreigner in listOfForeigners:
                    if foreigner['online'] == 'TRUE' and self.is_geo_position_in_circle(userData, userData['foreignerradius'], foreigner):
                        listofAllWhoCanSee.append({'jid': foreigner['jid'], 'relation': 'foreigner'})
                    else:
                        pass
            except:
                    print "Could not fetch foreigners"
                    
        #set pending relation all foreigners and acquaintances who are pending friends
        listOfPendingFriends = self.dbI.get_all_friendship_pendings_to(jID)
        if listOfPendingFriends != False:
            try:
                for pendJID in listofAllWhoCanSee:
                    if pendJID['relation'] != 'friend' and self.is_listOfPendingFriends(pendJID['jid'], listOfPendingFriends):
                        pendJID['relation'] = 'pending'
            except:
                print "Could not set penders"

        return listofAllWhoCanSee
    
    def is_listOfPendingFriends(self, jID, listOfPendingFriends):
        '''
        Test if the jid is in the list which should be a list of sqlite3.Row objects
        '''
        for r in listOfPendingFriends:
            if r['jid'] == jID:
                return True
        return False

    def is_geo_position_in_circle(self, userPosition, radius, othersPosition):
        '''
        Tests if the othersPosition is in the circle given by userPosition and radius
        '''
        if radius == 0:
            return False
        
        dist = math.sqrt((othersPosition['Lat'] - userPosition['Lat']) ** 2 + (othersPosition['Long'] - userPosition['Long']) ** 2)
        if dist <= radius:
            return True
        
        return False
    
    def share_geo_loc(self, senderJID, receiverUsername, geodata):
        '''
        The user senderJID wants to share a location with the user with given recevierUsername.
        
        If the receiving user is not online he/she will receive an email with a link to google maps.
        '''
        
        #get receiving user status
        receiverJID = receiverUsername + "@" + SERVER_DOMAIN
        status = self.dbI.get_user_availability(receiverJID)
        if status == False:
            return
        
        #is user offline?
        if status['online'] == 'FALSE':
            #check configuration for notifications...
            receiverSettings = self.dbI.get_settings(receiverJID)
            if receiverSettings != False:
                if receiverSettings['send_mail_notifications']:
                    #send mail
                    try:
                        msg = self.create_email_message(receiverUsername, status['email'], geodata)
                        if msg != False:
                            sendMail(NOREPLY_MAIL_ADDRESS,status['email'],msg)
                    except:
                        print "Could not deliver mail to " + status['email']
                 
        #send location via xmpp (done by server interaction)
        return        
    
    def create_email_message(self, username, recevierMailAddress, geodata):
        try:
            msgRoot = MIMEMultipart('alternative')
            msgRoot['Subject'] = "Marauder's Map: Location Notification"
            msgRoot['To'] = recevierMailAddress
            msgRoot['From'] = NOREPLY_MAIL_ADDRESS   
            
            #plain text versio
            plainMessage = username + ' wants to share a location with you. Click on link to see map: '
            plainMessage += 'http://maps.google.com/maps?q=%s,%s' % (geodata['lat'], geodata['lon'])
            msgPlainText = MIMEText(plainMessage, 'plain')
            
            #html version
            htmlMessage = '<div align="center"> \
                                <p>' + username + ' wants to share the followring location with you: </p> \
                                <img src="http://maps.google.com/staticmap?zoom=15&size=512x512&maptype=mobile&markers=%s,%s,green&sensor=false&key=%s"> \
                                <p><a href="http://maps.google.com/maps?q=%s,%s">Show on Google Maps</a></p> \
                            </div>' % (geodata['lat'], geodata['lon'], GOOGLE_MAPS_API_KEY, geodata['lat'], geodata['lon'])
            msgHtmlText = MIMEText(htmlMessage, 'html')
            
            msgRoot.attach(msgPlainText)
            msgRoot.attach(msgHtmlText)
            
                    
            return msgRoot.as_string()
        except:
            return False
    
    #Friendships related
    
    def create_friendship(self, callerJID, friendJID):
        '''
        Creates a friendship between callerJID and friendJID if it does not exist yet
        '''
        return self.dbI.insert_friendship(callerJID, friendJID)
    
    def destroy_friendship(self, callerJID, lostFriendJID):
        '''
        Delete a friendship on database if it exist
        '''
        return self.dbI.delete_friendship(callerJID, lostFriendJID)