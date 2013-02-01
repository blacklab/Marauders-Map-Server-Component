#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.component import Component

import os
import sys
sys.path.append(os.getcwd())

from maraudersserver import MaraudersProtocol
from Backend.MaraudersMapBackend import MaraudersMapBackEnd

from Backend.ServerSettings import *

'''
This file needs to be called with twisted to run the backend. It does not run as a daemon yet.
'''

application = service.Application("Marauders Map")

# initialize backend caontaining logic
back = MaraudersMapBackEnd()

# initialize component
xmppcomponent = Component(XMPP_SERVER_IP_ADDRESS, 5275, SERVER_JID, SERVER_COMPONENT_PASSWORD)
xmppcomponent.logTraffic = LOG_TRAFFIC_FLAG
echobot = MaraudersProtocol(back.sv)
echobot.setHandlerParent(xmppcomponent)
xmppcomponent.setServiceParent(application)
