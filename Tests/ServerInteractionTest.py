#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from Backend.MaraudersMapBackend import MaraudersMapBackEnd
from twisted.internet import reactor

__author__="katze"
__date__ ="$04.03.2010 12:19:53$"

import unittest

class ServerInteractionTest(unittest.TestCase):

    '''
    NOTE: Some changes prevent this test from running without a FAIL. Use breakpoints for Debugging.
    '''
    
    def setUp(self):
        self.jID = "iphone@maraudersserver.com"
        self.back = MaraudersMapBackEnd()

    def test_updatesettingsontrue(self):
        '''
        tests the updatesettingsfunction, if returns true if settings are correct
        '''
        settings = {"share_buddysight_friends_flag":0, "share_buddysight_acquaintances_flag":0, "share_buddysight_foreigners_flag":0}
        self.assertTrue(self.back.sv.update_settings("moony@maraudersserver.com", settings))

    def test_updatesettingsonfalse(self):
        '''
        tests the updatesettingsfunction, if returns false if settings are wrong
        '''
        #settings = {"friendradius": 500,"foreignerradius": 500, "friendoffriendoffriendradius":500}
        #self.assertFalse(self.back.sv.update_settings(self.jID, settings))
        pass
        
    def test_getSettings(self):
        '''
        tests if all user settings are retrieved from db in right form
        '''
        settings = self.back.sv.get_settings('moony@maraudersserver.com')
        
        print settings
        
    def test_getUserInfo(self):
        '''
        test if the user infos are fetched right
        '''
        userInfos = self.back.sv.get_user_info(self.jID,'moony@maraudersserver.com')
        print userInfos
        #self.assertEqual(userInfos['name'], 'Jobs')
        
    def test_createFriendship(self):
        r = self.back.sv.create_friendship('moony@maraudersserver.com',self.jID)
        self.assertTrue(r)
        
    def test_getUserInfoWithAquaintace(self):
        '''
        Test the highly complex UserInfowithAquaintance
        '''
        userInfos = self.back.log.get_user_info(self.jID, 'padfoot@maraudersserver.com')
        
        print userInfos
        
    def test_sendAvatar(self):
        '''
        Test server interaction send_avatar
        '''
        self.back.sv.save_avatar('prongs@maraudersserver.com', 'buddydata')
        
    def test_shareGeoLoc(self):
        '''
        Test if a user receives an email wit link to Google Maps on sharing geoloc if he/she is offline.
        '''
        pass
        #self.back.sv.share_geo_loc('padfoot@maraudersserver.com', 'moony', {'lat':51.97117, 'lon':7.599879, 'accuracy':100})
        #reactor.run()
        #reactor.stop()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
