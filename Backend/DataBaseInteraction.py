#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from ServerSettings import *

import sqlite3

class DataBaseInteraction(object):

    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    c = connection.cursor()
    
    def __init__(self, back):
        self.back = back
        
    #Fuer wenn wir mal Bilder in der DB speichern moechten:
    def save_images_in_db(self, image, long, lat, acc):
        '''
        Saves an image as base64 in db
        '''
        try:
            self.c.execute('INSERT INTO Images (image, long, lat, acc) VALUES (?, ?, ?, ?))', (image, long, lat, acc, ))
            self.c.commit()
            return True
        except:
            return False
    
    def get_image_from_db(self, long, lat):
        '''
        Retrieves an image from db at given Geodata
        Returns an image as Base64 string
        '''
        self.c.execute("SELECT image FROM Images WHERE long = ?, lat = ?", (long, lat, ))
        try:
            d = self.c.fetchall()
            if d == None:
                return False
            else:
                return d
        except:
            return False
        
        
        
    #Geolocation related

    def get_radii_and_geodata_for_user(self, jID):
        '''
        Looks up the friends visibility radius, friend of friends radius and the foreigner radius 
        and the position (geodata) of a user.
         
        Returns a sqlite.Row object
        '''
        self.c.execute("SELECT jid, online, Long, Lat, Acc, friendradius, acquaintanceradius, foreignerradius \
                    FROM GeoLoc, UsersSettings, Users \
                    WHERE GeoLoc.user_id = UsersSettings.user_id AND UsersSettings.user_id = Users.id AND jid = ?", (jID,))
        try:
            d = self.c.fetchone()
            if d == None:
                return False;
            else:
                return d
        except:
            return False

    def refresh_geo_loc(self, jID, long, lat, acc):
        '''
        Updates longitude, latitude and accuracy for a given jid
        '''
        try:
            self.c.execute("UPDATE GeoLoc SET Long = ?, Lat = ?, Acc = ? WHERE EXISTS (SELECT jid FROM Users WHERE GeoLoc.user_id = Users.id AND Users.jid = ?)", (long, lat, acc, jID))
            self.connection.commit()
        except Exception, e:
            print "Exception: Database Commit failed (refresh_geo_loc)", e
        return True

    def get_all_friends_of(self, jID):
        '''
        Fetches jid and position for all friends of the user with the given jid
        
        @rtype: a list of sqlite.Row objects with infos about friends
        '''
        try:
            self.c.execute("SELECT friend.jid, friend.online, Long, Lat, Acc FROM Users AS user, Users AS friend, Friendships, GeoLoc \
                        WHERE user.id = Friendships.user_id AND friend.id = Friendships.friend_id AND friend.id = GeoLoc.id AND Friendships.Pending = 'False' AND user.jid = ?", (jID,))
            friends = self.c.fetchall()
            return friends
        except:
            return False
        
    def get_all_acquaintances_of(self, jID):
        '''
        Fetches jid and position for all friends of the friends of the user (acquaintances) with given jid. 
        
        @rtype: a list of sqlite.Row objects with infos about friends of friends
        '''
        try:
            self.c.execute("SELECT friendoffriends.jid, friendoffriends.online, Long, Lat, Acc \
                            FROM Users AS user, Users AS friendoffriends, Friendships AS userFriendships, Friendships AS friendOfUserFriendships, GeoLoc \
                            WHERE user.id = userFriendships.user_id AND userFriendships.friend_id = friendOfUserFriendships.user_id AND userFriendships.Pending = 'False' \
                            AND friendoffriends.id = friendOfUserFriendships.friend_id AND friendoffriends.id = GeoLoc.id AND friendOfUserFriendships.Pending = 'False' \
                            AND friendoffriends.id NOT IN (SELECT friend.id FROM Users AS friend, Friendships WHERE user.id = Friendships.user_id AND friend.id = Friendships.friend_id AND Friendships.Pending = 'False' ) \
                            AND friendoffriends.jid != ? AND user.jid = ?", (jID,jID,))
            fof = self.c.fetchall()
            return fof
        except:
            return False

    def get_all_foreigners_of(self, jID):
        '''
        Fetches jid and position for all users without the given jid and returns them
        
        @rtype: a list of sqlite.Row objects
        '''
        try:
            self.c.execute(" SELECT foreigners.jid, foreigners.online, Long, Lat, Acc FROM Users as foreigners, GeoLoc \
                                WHERE foreigners.id NOT IN\
                                    (SELECT friendoffriends.id FROM Users AS user, Users AS friendoffriends, Friendships AS userFriendships, Friendships AS friendOfUserFriendships, GeoLoc\
                                                         WHERE user.id = userFriendships.user_id AND userFriendships.friend_id = friendOfUserFriendships.user_id AND userFriendships.Pending = 'False'\
                                                         AND friendoffriends.id = friendOfUserFriendships.friend_id AND friendOfUserFriendships.Pending = 'False' AND friendoffriends.id = GeoLoc.id AND user.jid = ?) \
                                AND foreigners.id NOT IN \
                                    (SELECT friend.id FROM Users AS user, Users AS friend, Friendships WHERE user.id = Friendships.user_id AND friend.id = Friendships.friend_id AND Friendships.Pending = 'False' AND user.jid = ?) \
                                AND GeoLoc.user_id = foreigners.id AND foreigners.jid !=  ?",(jID,jID,jID,))
            foreigners = self.c.fetchall()
            return foreigners
        except:
            return False
        
    def get_all_friendship_pendings_to(self, jID):
        '''
        Fetches jid of all users who have a pending friend request for user with jID
        '''
        try:
            self.c.execute("SELECT friend.jid FROM Users AS user, Users AS friend, Friendships \
                                WHERE user.id = Friendships.user_id AND friend.id = Friendships.friend_id AND Friendships.Pending = 'True' AND Friendships.sender_id != user.id AND user.jid = ?", (jID,))
            return self.c.fetchall()
        except:
            return False
        
    #User and account info
    
    def get_jid_of_all_users(self):
        '''
        Retrieves the JIDs of all users in db.
        
        @rtype: list of sqlite.Row object
        '''
        try:
            self.c.execute("SELECT jid FROM Users")
            return self.c.fetchall()           
        except:
            return list()
        
    def get_user_info(self, jID):
        '''
        Retrieves the infos about a user form UserInfo table for get settings
        
        @rtype: a sqlite.Row object
        '''
        try:
            self.c.execute("SELECT jid, email, name, first_name, avatar FROM UserInfo, Users WHERE UserInfo.user_id = Users.id AND jid = ?",(jID,))
            d = self.c.fetchone()
            if d == None:
                return False
            return d
        except:
            return False
        
    def get_user_info_with_aquaintace_info(self, callerjID, aboutjID):
        '''
        Retrieves the infos about a user form UserInfo table and the aquaintance info
        
        @rtype: a sqlite.Row object
        '''
        try:
            self.c.execute("SELECT about.jid, about.email, userinfo.name, userinfo.first_name, userinfo.avatar, aquaintanceInfo.name AS acquaintance_over_name, aquaintanceInfo.first_name AS acquaintance_over_first_name, acquaintanceover.jid AS acquaintance_over_jid FROM UserInfo AS userinfo, UserInfo AS aquaintanceInfo, Users AS about, Users AS acquaintanceover \
                            WHERE userinfo.user_id = about.id AND about.jid = ? AND aquaintanceInfo.user_id = acquaintanceover.id AND acquaintanceover.jid IN \
                            (SELECT aquaintanceover.jid FROM Users AS user, Users AS friendoffriends, Users AS aquaintanceover, Friendships AS userFriendships, Friendships AS friendOfUserFriendships \
                                    WHERE user.id = userFriendships.user_id AND userFriendships.friend_id = friendOfUserFriendships.user_id AND userFriendships.Pending = 'False' \
                                    AND friendoffriends.id = friendOfUserFriendships.friend_id AND friendOfUserFriendships.Pending = 'False' AND aquaintanceover.id = userFriendships.friend_id \
                                    AND friendoffriends.jid != ? AND user.jid = ?) \
                            AND  ? IN (SELECT friendoffriends.jid FROM Users AS user, Users AS friendoffriends, Friendships AS userFriendships, Friendships AS friendOfUserFriendships \
                                    WHERE user.id = userFriendships.user_id AND userFriendships.friend_id = friendOfUserFriendships.user_id AND userFriendships.Pending = 'False' \
                                    AND friendoffriends.id = friendOfUserFriendships.friend_id AND friendOfUserFriendships.Pending = 'False' \
                                    AND friendoffriends.jid != ? AND user.jid = ?) \
                            AND  ? NOT IN (SELECT friend.jid FROM Users AS user, Users AS friend, Friendships, GeoLoc \
                                WHERE user.id = Friendships.user_id AND friend.id = Friendships.friend_id AND friend.id = GeoLoc.id AND Friendships.Pending = 'False' AND user.jid = ?)",(aboutjID, callerjID, callerjID, aboutjID, callerjID, callerjID, aboutjID, callerjID))
            d = self.c.fetchone()
            if d == None:
                self.c.execute("SELECT jid, name, first_name, avatar, email FROM UserInfo, Users WHERE UserInfo.user_id = Users.id AND jid = ?",(aboutjID,))
                e = self.c.fetchone()
                if e == None:
                    return False
                return e
            return d
        except:
            return False
        
        
    def update_user_first_name(self, jID, firstName):
        '''
        Updates the first name of a user in his/her profile.
        '''
        try:
            self.c.execute("UPDATE UserInfo SET first_name = ? WHERE EXISTS (SELECT jid FROM Users WHERE UserInfo.user_id = Users.id AND Users.jid = ?)", (firstName, jID, ))
            self.connection.commit()
        except:
            return False
        return True 
    
    def update_user_name(self, jID, name):
        '''
        Updates the first name of a user in his/her profile.
        '''
        try:
            self.c.execute("UPDATE UserInfo SET name = ? WHERE EXISTS (SELECT jid FROM Users WHERE UserInfo.user_id = Users.id AND Users.jid = ?)", (name, jID, ))
            self.connection.commit()
        except:
            return False
        return True  
    
    def update_user_avatar(self, jID, avatarData):
        '''
        Updates the avatar field in UserInfo table.
        
        avatarData is base64 encoded
        '''
        try:
            self.c.execute("UPDATE UserInfo SET avatar = ? WHERE EXISTS (SELECT jid FROM Users WHERE UserInfo.user_id = Users.id AND Users.jid = ?)", (avatarData, jID, ))
            self.connection.commit()
        except:
            return False
        return True
    
    def get_avatar_for_username(self, ownerJID):
        '''
        Looks up the avatar for the user with given userName.
        
        @param ownerName: the jid of the user whose avatar should be returned
        
        @rtype: a sqlite.Row object
        '''
        try:
            self.c.execute("SELECT avatar FROM UserInfo, Users WHERE UserInfo.user_id = Users.id AND jid = ?",(ownerJID,))
            e = self.c.fetchone()
            if e == None:
                return False
            return e           
        except:
            return False
      
    def update_user_email_address(self, jID, emailaddress):
        '''
        Updates the email address of a user with given jID
        '''
        try:
            self.c.execute("UPDATE Users SET email = ? WHERE jid = ?", (emailaddress, jID, ))
            self.connection.commit()
        except:
            return False
        return True       
          
    #User Availability
    
    def update_user_availability(self, jid, status):
        '''
        Updates the availability of a user. status = TRUE means online and FALS menas offline.
        
        @type jid: str
        @type status: str
        '''
        try:
            self.c.execute("UPDATE Users SET online = ? WHERE jid = ?",(status, jid,))
            self.connection.commit()       
        except:
            return False
        return True
    
    def get_user_availability(self, userJID):
        '''
        Fetches the online status of a user form database.
        
        @rtype: a sqlite.Row object
        '''
        try:
            self.c.execute("SELECT online, email FROM Users WHERE jid = ?",(userJID,))
            e = self.c.fetchone()
            if e != None:
                return e    
        except:
            return False
        return False
    
    #User Settings
    
    def get_settings(self, jID):
        '''
        Retrieves usersettings of a user with given jID

        @rtype: a sqlite.Row object
        '''
        try:
            self.c.execute("SELECT jid, friendradius, acquaintanceradius, foreignerradius, send_mail_notifications, show_name, show_email, share_buddysight_friends, share_buddysight_acquaintances, share_buddysight_foreigners \
                    FROM UsersSettings, Users \
                    WHERE UsersSettings.user_id = Users.id AND jid = ?", (jID,))
            d = self.c.fetchone()
            if d == None:
                return False;
            return d
        except:
            return False

    def update_acquaintances_radius(self, jID,acquaintancesradius):
        '''
        Updates the acquaintances radius for user with given jID
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET acquaintanceradius = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (acquaintancesradius, jID, ))
            self.connection.commit()
        except:
            return False
        return True

    def update_friends_radius(self, jID,friendsradius):
        '''
        Updates the friends radius for user with given jID
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET friendradius = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (friendsradius, jID, ))
            self.connection.commit()
        except:
            return False
        return True

    def update_foreigners_radius(self, jID, foreignersradius):
        '''
        Updates the foreigners radius for user with given jID
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET foreignerradius = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (foreignersradius, jID, ))
            self.connection.commit()
        except:
            print "except was called"
            return False
        return True
    
    def update_user_mail_notifications(self, jID, notification_flag):
        '''
        Updates user settings for sending email notifications
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET send_mail_notifications = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (notification_flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True
    
    def update_user_share_buddysight_friends_flag(self, jID, flag):
        '''
        Updates user settings for showing buddy sight to friends
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET share_buddysight_friends = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True
    
    def update_user_share_buddysight_acquaintances_flag(self, jID, flag):
        '''
        Updates user settings for showing buddy sight to acquaintances
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET share_buddysight_acquaintances = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True

    def update_user_share_buddysight_foreigners_flag(self, jID, flag):
        '''
        Updates user settings for showing buddy sight to foreigners
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET share_buddysight_foreigners = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True   
    
    def update_user_show_name_flag(self, jID, flag):
        '''
        Updates user settings for showing user names to others
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET show_name = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True
    
    def update_user_show_email_flag(self, jID, flag):
        '''
        Updates user settings for showing user email address to others
        '''
        try:
            self.c.execute("UPDATE UsersSettings SET show_email = ? WHERE EXISTS (SELECT jid FROM Users WHERE UsersSettings.user_id = Users.id AND Users.jid = ?)", (flag, jID, ))
            self.connection.commit()
        except:
            return False
        return True
    
    #Friendships related
    
    def insert_friendship(self, firstFriendJID, secondFriendJID):
        '''
        Insert two rows with the id of the users with the JIDs into Friendships table
        '''
        try:
            self.c.execute("UPDATE Friendships SET Pending = 'False' WHERE EXISTS ( SELECT * FROM Users As user, Users AS friend WHERE user.jid = ? AND friend.jid = ? AND Friendships.sender_id != user.id \
                            AND ( (user.id =  Friendships.user_id AND friend.id = Friendships.friend_id) OR (user.id =  Friendships.friend_id AND friend.id = Friendships.user_id)))",(firstFriendJID,secondFriendJID,))
            self.c.execute("INSERT INTO Friendships ('user_id', 'friend_id', 'Pending', 'sender_id') \
                            SELECT user.id, friend.id, 'True', sender.id FROM Users AS user, Users AS friend, Users AS sender \
                            WHERE sender.jid = ? AND ( (user.jid = ? AND friend.jid = ?) OR (friend.jid = ? AND user.jid = ?) ) \
                                AND NOT EXISTS (SELECT * FROM Friendships WHERE Friendships.user_id = user.id AND Friendships.friend_id = friend.id)", (firstFriendJID, firstFriendJID, secondFriendJID, firstFriendJID, secondFriendJID,))
        except:
            return False
        return True
    
    def delete_friendship(self, firstFriendJID, secondFriendJID):
        '''
        Delete both rows form the Friendship table with the id of the users with the given JIDs.
        '''
        try:
            self.c.execute("DELETE FROM Friendships WHERE EXISTS (SELECT user.id FROM Users As user, Users As friend \
                                WHERE (user .id = Friendships.user_id OR user.id = Friendships.friend_id) AND user.jid = ? \
                                AND (friend.id = Friendships.user_id OR friend.id = Friendships.friend_id) AND friend.jid = ?)",(firstFriendJID,secondFriendJID,))
        except:
            return False
        return True