#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8
import uuid
from twisted.words.xish import domish
from wokkel.subprotocols import IQHandlerMixin, XMPPHandler
from twisted.words.protocols.jabber import jid


NS_IMAGE_QUERY = 'urn:xmpp:picture'
IQ_GET = '/iq[@type="get"]'
IQ_SET = '/iq[@type="set"]'

IQ_IMAGE_QUERY = IQ_GET + '/imagequery[@xmlns="' + NS_IMAGE_QUERY + '"]'


class ImageQuery(XMPPHandler):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        print 'Hallo aus Const'

    def connectionInitialized(self):
        print "connectionInit"
        self.xmlstream.addObserver(IQ_IMAGE_QUERY, self._onImageQuery)
        print "connectionInitEnd"
        
    def _onImageQuery(self, iq):
        print "onImageQuery..."
        if iq.handled == True:
            print "Already..."
            return 
        try:
            #sender = jid.JID(iq["from"])
            #receiver = jid.JID(iq["to"])
            print "Sending..."
            self.send(iq)
        except: # the location query request has not all elements
            print "Failed Sending..."
            return
                