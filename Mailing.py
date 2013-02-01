#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8
from twisted.mail.smtp import sendmail

from Backend.ServerSettings import *

def sendMail(fromAddress, toAddress, message):
    '''
    This function is used to send an eMail through a remote SMTP server without authentication.
    It uses twisted for sending.
    
    SUGGESTIONS: It seems that twisted builds a factory and shuts it down again every time an email is sent.
    This might draw some performance.
    
    @type fromAddress: string
    @type toAddress: string
    @type message: string
    '''
    dfr = sendmail(MAIL_SERVER, fromAddress, toAddress, message)
    def success(r):
        print r
    def error(e):
        print e
    dfr.addCallback(success)
    dfr.addErrback(error)


    






