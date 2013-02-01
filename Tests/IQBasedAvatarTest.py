#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

import unittest
from twisted.words.xish import domish

from XEP.IQBasedAvatar import IQBasedAvatar, AvatarResult

class Test(unittest.TestCase):

    '''
    NOTE: Some changes prevent this test from running without a FAIL. Use breakpoints for Debugging.
    '''

    def setUp(self):
        self.iqbasedavatar = IQBasedAvatar()
        
        #build test set avatar stanza
        self.iq = domish.Element((None, 'iq'))
        self.iq['id'] = '1234'
        self.iq['type'] = 'set'
        self.iq['from'] = 'prongs@maraudersserver.com'
        self.iq['to'] = 'prongs@back.maraudersserver.com'
        
        query = self.iq.addElement(('storage:client:avatar', 'query'))
        data = query.addElement('data')
        data['mimetype'] = 'image/png'
        data.addContent('Base64 Encoded Data')
        
        print self.iq.toXml()

    def tearDown(self):
        pass

    #test on receive a set avatar stanza
    def test_onSetAvatar(self):
        self.iqbasedavatar.saveAvatar = self.onSaveAvatar
        self.iqbasedavatar._onSetAvatar(self.iq)
    
    def onSaveAvatar(self, ownerJID, avatarData):
        self.assertEqual(ownerJID.userhost(), 'prongs@maraudersserver.com')
        self.assertEqual(avatarData, 'Base64 Encoded Data')

    def test_AvatarResult(self):
        r = AvatarResult(1234, 'moony@maraudersserver.com', 'prongs@maraudersserver.com', 'Base64 Encoded Data')
        print r.toXml()
        pass
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()