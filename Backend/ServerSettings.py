#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

# Server Domain
SERVER_DOMAIN = "maraudersserver.com"
SERVER_JID = "back@maraudersserver.com"
SERVER_COMPONENT_PASSWORD = "iphonemac"
XMPP_SERVER_IP_ADDRESS = "127.0.0.1" # right now OpenFire on localhost

LOG_TRAFFIC_FLAG = True

# Mail Server
MAIL_SERVER = "localhost"
NOREPLY_MAIL_ADDRESS = 'marauders@uni-muenster.de'#'noreply@maraudersserver.com'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "ABCD"

# The database file
DB_FILE = "maraudersmap.sqlite"

# Minimum and maximum for radii
MIN_RADIUS = 0.0
MAX_RADIUS = 20000.0

# Language variables

#visibility settings
VISIBILITY_HEADER = 'Visibility Settings'
VISIBILITY_DESCRIPTION = 'Sets the range of your visibility. For example, if your friend has set his visibility to 500m, you will be able to see him if you are not more than 500 m away from him. Set your own visibility to a reasonable value to be visible to him as well. Acquaintances are friends of your own friends.'

VISIBLITY_FRIENDS_RADIUS = 'Friend Radius'
VISIBILITY_ACQUAINTANCE_RADIUS = 'Acquaintance Radius'
VISIBILITY_FOREIGNER_RADIUS = 'Foreigner Radius'

#notification settings
NOTIFICATION_SETTINGS_HEADER = 'Notification Settings'
NOTIFICATION_SETTINGS_DESCRIPTION = 'Here you can set whether you want to receive an email on a certain event. E.g. if you are not online and some one shares a location with you, you receive an email.'

NOTIFICATION_SETTINGS_EMAIL_NOTIFICATIONS = 'Location E-mails'

#buddy sight settings
BUDDYSIGHT_SETTINGS_HEADER = 'Buddy Sight Settings'
BUDDYSIGHT_SETTINGS_DESCRIPTION = 'Buddy Sight is a way for you to show other people where you are and what you see. These options set who will receive your buddy sight images. \n If you switch Friends on, all of your friends will receive your buddy sight images even if they are not in your Friend Radius. If you switch Acquaintances or Foreigners on, all your acquaintances or foreigners in your Acquaintance Radius or Foreigner Radius will receive your buddy sight images.'

BUDDYSIGHT_SETTINGS_SHARE_FRIENDS = 'Friends'
BUDDYSIGHT_SETTINGS_SHARE_ACQUAINTANCES = 'Acquaintances'
BUDDYSIGHT_SETTINGS_SHARE_FOREIGNERS = 'Foreigners'

#profile view settings
PROFILE_VIEW_SETTINGS_HEADER = 'Profile View Settings'
PROFILE_VIEW_SETTINGS_DESCRIPTION = 'Here you can set whether a certain information is shown to a user when he views your profile.'

PROFILE_VIEW_SETTINGS_SHOW_NAME = 'Show Name'
PROFILE_VIEW_SETTINGS_SHOW_EMAIL = 'Show eMail Address'

PROFILE_SETTINGS_HEADER = 'Profile'
PROFILE_SETTINGS_DESCRIPTION = 'Here you can set details for your profile.'

PROFILE_SETTINGS_FIRST_NAME = 'First Name'
PROFILE_SETTINGS_NAME = 'Name'
PROFILE_SETTINGS_EMAIL_ADDRESS = 'eMail Address'

#general info view
GENERAL_INFO_HEADER = 'General Information'
GENERAL_INFO_DESCRIPTION = 'Details about the user whose profile you are viewing right now.'

GENERAL_INFO_BUDDYSIGHT = 'Buddy Sight'
GENERAL_INFO_FIRST_NAME = 'First Name'
GENERAL_INFO_NAME = 'Name'
GENERAL_INFO_EMAIL = 'E-Mail Address'
GENERAL_INFO_ACQUAINTANCE_OVER = 'Mutual friend'