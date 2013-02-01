#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

import inspect
from types import *
from Backend.ServerSettings import *
from twisted.words.xish import domish
from wokkel.subprotocols import XMPPHandler

NS_JABBER_RPC = 'jabber:iq:rpc'

IQ_SET = '/iq[@type="set"]'
IQ_RESULT = '/iq[@type="result"]'
IQ_ERROR = '/iq[@type="error"]'

IQ_CALL_METHOD_QUERY = IQ_SET + '/query[@xmlns="' + NS_JABBER_RPC + '"]'
IQ_RETURN_RESULT_QUERY = IQ_RESULT + '/query[@xmlns="' + NS_JABBER_RPC + '"]'
IQ_RETURN_ERROR_QUERY = IQ_ERROR + '/query[@xmlns="' + NS_JABBER_RPC + '"]'

class RPCResult(domish.Element):
    '''
    Forms an iq answer for the remote procedure call according to
    
    http://xmpp.org/extensions/xep-0009.html
    http://www.xmlrpc.com/spec
    '''
    
    #assume success for now
    def __init__(self, caller, rpcid, result):
        domish.Element.__init__(self, (None, 'iq'))
        self.result = result
        self.caller = caller
        self.rpcid = rpcid
        
        self._formResult()
        
    def _formResult(self):
        '''
        Create iq answer stanza
        '''
        
        self['type'] = 'result'
        self['to'] = self.caller
        self['from'] = SERVER_JID
        self['id'] = self.rpcid
        
        query = self.addElement((NS_JABBER_RPC,'query'))
        methodResponse = query.addElement('methodResponse')
        params = methodResponse.addElement('params')
        param = params.addElement('param')
        value = param.addElement('value')
        
        #append result to value
        value.addChild(self._getFormedValueFor(self.result))
        
    def _getFormedValueFor(self, value):
        '''
        Forms an xml element for given value and returns it
        '''
        #what type is value?
        if value == None:
            return self._getFormedStringValue("None")
        
        if isinstance(value, BooleanType):
            return self._getFormedBooleanValue(value)
        elif isinstance(value, IntType):
            return self._getFormedIntValue(value)
        elif isinstance(value, StringTypes):
            return self._getFormedStringValue(value)
        elif isinstance(value, FloatType):
            return self._getFormedFloatValue(value)
        elif isinstance(value, ListType):
            return self._getFormedListValue(value)
        elif isinstance(value, DictType):
            return self._getFormedDictValue(value)
        
    def _getFormedIntValue(self, value):
        '''
        Forms an xml element for xml rpc containing an integer
        '''
        try:
            formedValue = domish.Element((None, 'int'))
            formedValue.addContent("%d" % value)
            return formedValue
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue
        
    def _getFormedStringValue(self, value):
        '''
        Forms an xml element for xml rpc containing a string
        '''
        try:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("%s" % value)
            return formedValue
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue   
        
    def _getFormedFloatValue(self, value):  
        '''
        Forms an xml element for xml rpc containing a float
        '''
        try:
            formedValue = domish.Element((None, 'double'))
            formedValue.addContent("%f" % value)
            return formedValue
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue   
        
    def _getFormedBooleanValue(self, value):
        '''
        Forms an xml element for xml rpc containing a boolean
        '''
        try:
            formedValue = domish.Element((None, 'boolean'))
            if value:
                formedValue.addContent("1")
            else:
                formedValue.addContent("0")
            return formedValue
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue   
        
    def _getFormedListValue(self, value):
        '''
        Forms an xml element for xml rpc containing an array
        @type value: should be of type List
        '''
                
        try:
            arrayElement = domish.Element((None, 'array'))
            dataElement = arrayElement.addElement('data')
            for item in value:
                valueElement = dataElement.addElement('value')
                valueElement.addChild(self._getFormedValueFor(item))
            return arrayElement
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue 
        
    def _getFormedDictValue(self, value):
        '''
        Forms an xml element for xml rpc containing a struct
        @type value: should of type dictionary
        '''
        
        try:
            structElement = domish.Element((None, 'struct'))
            for key in value.keys():
                memberElement = structElement.addElement('member')
                memberElement.addElement('name', content = key)
                valueElement = memberElement.addElement('value')
                valueElement.addChild(self._getFormedValueFor(value[key]))
            return structElement
        except:
            formedValue = domish.Element((None, 'string'))
            formedValue.addContent("no value")
            return formedValue                    

class JabberRPC(XMPPHandler):
    '''
    Protocol implementation for Jabber-RPC (XEP-0009).
    
    See: http://xmpp.org/extensions/xep-0009.html and http://www.xmlrpc.com/spec
    
    The handler will listen to incoming RPC queries and will call the adequate function. 
    
    @ivar rpcFunctions: the functions which will be called by the remote procedure requests
    @type rpcFunctions: L{dict}
    
    Since rpcFunctions is a dictionary the methodNames don't have to be the same as the actual python method names.
    The names are mapped to their functions
    
    When the name of the first parameter of the function (method) which should be called is iq then the iq stanza will be passed on.    
    '''

    rpcFunctions = {}

    def __init__(self):
        '''
        Constructor
        '''
        
    def connectionInitialized(self):
        self.xmlstream.addObserver(IQ_CALL_METHOD_QUERY, self._onMethodCall)
        
    def registerMethodCall(self, name, method):
        '''
        Adds a rpc function which can be called via Jabber RPC
        
        @type name: String
        @type method: Function
        '''
        self.rpcFunctions[name] = method
        
    def _onMethodCall(self, iq):
        '''
        Handles RPC query. Trys to find function in rpcFunctions list.
        If a function (method) was found the parameters will be parsed and the function will be called with the parameters.
        
        If the function returns successfully the result will be send to the sender. On error and error stanza will be send. 
        '''
        
        if iq.hasAttribute('id') == False:
            return
        if iq.hasAttribute('from') == False:
            return
        
        rpcid = iq['id']
        fromJID = iq['from']
        
        #Check if query stanza is formed well
        try:
            methodName = str(iq.query.methodCall.methodName)
            parameters = iq.query.methodCall.params #<params>...</params>
        except:
            return
        
        #Check if requested method name is in function dictionary
        if methodName not in self.rpcFunctions.keys():
            return
        
        #Get function
        method = self.rpcFunctions[methodName]
        
        #Get parameters
        self.args = []
        
        for param in parameters.elements():
            arg = self._getEvaluatedValue(param.value)
            if arg != None:
                self.args.append(arg)
        
        #Call method       
        try:
            #get argument names of the method to be called
            argsOfMethod = inspect.getargspec(method).args
            if len(argsOfMethod) == 1:
                response = method(*self.args)
            elif argsOfMethod[1] == 'iq': #method wants iq stanza
                response = method(iq, *self.args)
            else:
                response = method(*self.args)
            
            #create response
            if response != None:
                result = RPCResult(fromJID, rpcid, response)
            else:
                result = RPCResult(fromJID, rpcid, True)
            self.send(result)
        except:
            return
    
    def _getEvaluatedValue(self, value):
        '''
        Decides what type value is and returns value as identified type.
        Returns None if value could not be evaluated.
        
        @param value: The <value>..</value> Element.
        @type value: C{Element} see twisted.words.xish
        
        @param parameterList: The argument list the evaluated value will be appended to
        @type parameterList: L{List}
        '''
        
        if value == None:
            return
        
        #Check type of value. Is child i4, int, boolean, string, double, sturct or array
        # base64 and dateTime.iso8601 are not supported yet
        if value == None:
            return
        elif value.i4 != None: #value is of type int
            try:
                i = int(str(value.i4))
                return i
            except:
                return
        elif value.int != None: #value is of type int
            try:
                i = int(str(value.int))
                return i
            except:
                return
        elif value.string != None: #value is of type string
            try:
                s = unicode(value.string)
                return s
            except:
                return
        elif value.double != None: #value is of type double
            try:
                f = float(str(value.double))
                return f
            except:
                return
        elif value.boolean != None: #value is of type boolean
            try:
                return int(str(value.boolean))
            except:
                return
        elif value.base64!= None: #value is of type base64. Not supported yet
            return
        elif value.struct != None: #value is of type struct
            try:
                s = self._getEvaluatedStruct(value.struct)
                return s
            except:
                return
        elif value.array != None: #value is of type array
            try:
                a = self._getEvaluatedArray(value.array)
                return a
            except:
                return
        else: #No type (or dateTime.iso8601) was given. Assume string
            try:
                s = unicode(value)
                return s
            except:
                return        
    
    def _getEvaluatedStruct(self, structElement):
        '''
        Structs are realized as dictionaries
        
        @param struct: The value type is struct. <struct>...</struct>
        @type struct: C{Element}
        
        @param parameterList: The argument list the evaluated value will be appended to
        @type parameterList: L{List}
        '''
        
        #create dictionary
        evaluatedDictionary = {}
        
        for member in structElement.elements():
            if member.name != "member":
                pass
            try:
                #get member name and value
                memberName = str(member.__getattr__('name')) # element.name is already taken
                memberValue = self._getEvaluatedValue(member.value)
                
                #append them to dictionary
                evaluatedDictionary[memberName] = memberValue
            except:
                pass
            
        return evaluatedDictionary
        
    def _getEvaluatedArray(self, arrayElement):
        '''
        Arrays are realized as lists. Parses children of array element and appends them to new created array.
        
        Returns array.
        
        @param array: The value type is array. Evaluate now array
        @type array: C{Element}
        
        @param parameterList: The argument list the evaluated value will be appended to
        @type parameterList: L{List}
        '''
        
        if arrayElement.data == None:
            return
        
        #the evaluated array
        evaluatedArray = []
        
        for value in arrayElement.data.elements():
            if value.name != "value":
                pass
            try:
                v = self._getEvaluatedValue(value)
                evaluatedArray.append(v)
            except:
                pass
            
        return evaluatedArray