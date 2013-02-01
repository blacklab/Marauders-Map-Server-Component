#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

import unittest
from twisted.words.xish import domish
from XEP.locationquery import LocationQuery, ShareGeoLocMessage 

class LocationQueryTest(unittest.TestCase):

    '''
    NOTE: Some changes prevent this test from running without a FAIL. Use breakpoints for Debugging.
    '''
    
    def setUp(self):
        self.locquery = LocationQuery()

    def test_onLocationShare(self):
        #build iq
        self.iq = domish.Element((None, 'iq'))
        self.iq['id'] = '1234'
        self.iq['type'] = 'set'
        self.iq['from'] = 'prongs@maraudersserver.com'
        self.iq['to'] = 'prongs@back.maraudersserver.com'
        
        locationqueryElement = self.iq.addElement(('urn:xmpp:locationquery:0', 'locationquery'))
        locationqueryElement.addElement('lat', content = '70')
        locationqueryElement.addElement('lon', content = '100')
        locationqueryElement.addElement('accuracy', content = '20')
        locationqueryElement.addElement('region', content = 'Münsterland')
        
        print self.iq.toXml()
        
        #add callback
        self.locquery.onLocationShare = self.onLocationShareCallback
        
        #call _onLocationShare
        self.locquery._onLocationShare(self.iq)
        pass
    
    def onLocationShareCallback(self, senderJID, receiverUsername, geodata, iq):
        print geodata
        
    def test_onLocationQuery(self):
        #build iq
        self.iq = domish.Element((None, 'iq'))
        self.iq['id'] = '1234'
        self.iq['type'] = 'get'
        self.iq['from'] = 'prongs@maraudersserver.com'
        self.iq['to'] = 'prongs@back.maraudersserver.com'
        
        locationqueryElement = self.iq.addElement(('urn:xmpp:locationquery:0', 'locationquery'))
        locationqueryElement.addElement('lat', content = '70')
        locationqueryElement.addElement('lon', content = '100')
        locationqueryElement.addElement('accuracy', content = '20')
        locationqueryElement.addElement('region', content = 'Münsterland')
        
        #add callback
        self.locquery.onLocationShare = self.onLocationQueryCallback
        
        #call _onLocationShare
        self.locquery._onLocationQuery(self.iq)
        pass
    
    def onLocationQueryCallback(self, senderJID, geodata, iq):
        print geodata
        
    def test_ShareGeoLocMessage(self):
        geoData = dict()
        geoData['lat'] = 70
        geoData['region'] = 'Münsterland'
        geoMessage = ShareGeoLocMessage('prongs@maraudersserver.com', 'prongs@maraudersserver.com', geoData)
        print geoMessage.toXml()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'LocationQueryTest.test_onLocationShare']
    unittest.main()