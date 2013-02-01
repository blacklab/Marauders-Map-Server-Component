#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - 2013 Karsten Jeschkies <jeskar@web.de>
# Licensed under the MIT License - http://opensource.org/licenses/MIT

# coding=utf-8

import unittest
from twisted.words.xish import domish

from XEP.jabberrpc import JabberRPC, RPCResult


class JabberRPCTest(unittest.TestCase):

    iq = None

    def setUp(self):
        self.jaberrpc = JabberRPC()
        
        #build test jabber rpc stanza
        print "Prepare test"
        self.iq = domish.Element((None, 'iq'))
        self.iq['id'] = '1234'
        self.iq['from'] = 'iphone@maraudersserver.com'
        query = self.iq.addElement('query')
        mc = query.addElement('methodCall')
        mc.addElement('methodName', content = 'functionToCall')
        params = mc.addElement('params')
        
        nameParam = params.addElement('param')
        nameValue = nameParam.addElement('value')
        nameValue.addElement('string', content = "Lukas")
        
        ageParam = params.addElement('param')
        ageValue = ageParam.addElement('value')
        ageValue.addElement('int', content = "%d" % 8)
        
        hobbiesParam = params.addElement('param')
        arrayValue = hobbiesParam.addElement('value')
        array = arrayValue.addElement('array')
        data = array.addElement('data')
        v1 = data.addElement('value')
        v1.addElement('string', content = "Soccer")
        v2 = data.addElement('value')
        v2.addElement('string', content = "BASE Jumping")
        
        boolParam = params.addElement('param')
        boolValue = boolParam.addElement('value')
        boolValue.addElement('boolean', content = "%d" % 1)

    def test_onMethodCall(self):
        self.jaberrpc.rpcFunctions['functionToCall'] = self.functionToCall
        self.jaberrpc._onMethodCall(self.iq)
       
    #function called by onMethodCall 
    def functionToCall(self, name, age, hobbies, flag):
        #@type name: String
        #@type age: Int
        #@type hobbies: List
        print 'My name is ' + name
        print 'I am: '
        print age
        print 'My hobbies are: '
        print hobbies
        
        self.assertEqual(name, 'Lukas')
        self.assertEqual(age, 8)
        self.assertEqual(hobbies, ['Soccer','BASE Jumping'])  
        self.assertTrue(flag) 
        
    def test_getEvaluatedValueInt(self):       
        valueElement = self.iq.query.methodCall.params.children[1].value
        
        #call method
        intValue = self.jaberrpc._getEvaluatedValue(valueElement)
        
        #asserts
        self.assertEqual(intValue, 8)
        self.assertEqual(type(intValue), type(10))
        
    def test_getEvaluatedValueI4(self):
        #build xml element
        element = domish.Element((None, 'value'))
        element.addElement('i4', content = "%d" % 4)
        print element.toXml()
        
        #call method
        intValue = self.jaberrpc._getEvaluatedValue(element)
                
        #asserts
        self.assertEqual(intValue, 4) 
        self.assertEqual(type(intValue), type(4))
        
    def test_getEvaluatedValueString(self):       
        valueElement = self.iq.query.methodCall.params.children[0].value
        
        #call method
        stringValue = self.jaberrpc._getEvaluatedValue(valueElement)
        
        #asserts
        self.assertEqual(stringValue, "Lukas")
        self.assertEqual(type(stringValue), type("some string"))

    def test_getEvaluatedValueDouble(self):
        #build xml element
        element = domish.Element((None, 'value'))
        element.addElement('double', content = "%f" % 12.03)
        print element.toXml()
        
        #call method
        floatValue = self.jaberrpc._getEvaluatedValue(element)
        
        #asserts
        self.assertEqual(floatValue, 12.03)
        self.assertEqual(type(floatValue), type(12.3))
        
    def test_getEvaluatedValueBoolean(self):
        #build xml element
        element = domish.Element((None, 'value'))
        element.addElement('boolean', content = "1")
        print element.toXml()
        
        #call method
        booleanValue = self.jaberrpc._getEvaluatedValue(element)
        
        #asserts
        self.assertTrue(booleanValue)
        self.assertEqual(type(booleanValue), type(False))
        
    def test_getEvaluatedValueDefault(self):
        #build xml element
        element = domish.Element((None, 'value'))
        element.addContent("12")
        print element.toXml()
        
        #call method
        stringValue = self.jaberrpc._getEvaluatedValue(element)
        
        #asserts
        self.assertEqual(stringValue, "12")
        self.assertEqual(type(stringValue), type("testSomething"))
        
    def test_getEvaluatedArray(self):
        #build xml element
        element = domish.Element((None, 'array'))
        data = element.addElement('data')
        v1 = data.addElement('value')
        v1.addElement('int', content = "%d" % 4)
        v2 = data.addElement('value')
        v2.addElement('string', content = "hey there")
        
        #call method
        arrayValues = self.jaberrpc._getEvaluatedArray(element)
        
        #asserts
        self.assertEqual(arrayValues[0], 4)
        self.assertEqual(arrayValues[1], "hey there")
        
    def test_getEvaluatedStruct(self):
        #build xml element
        element = domish.Element((None, 'struct'))
        m1 = element.addElement('member')
        m1.addElement('name', content = 'age')
        v1 = m1.addElement('value')
        v1.addElement('int', content = "%d" % 8)
        
        m2 = element.addElement('member')
        m2.addElement('name', content = 'firstname')
        v2 = m2.addElement('value')
        v2.addElement('string', content = "Lukas")
        
        #call method
        sturctValues = self.jaberrpc._getEvaluatedStruct(element)
        
        #asserts
        self.assertEqual(sturctValues['age'], 8)
        self.assertEqual(sturctValues['firstname'], "Lukas")
        
    def test_RPCResult(self):
        result = [1,True, 'Lukas', {'alter':7, 'groesse':1.45}]
        rpcresult = RPCResult('moony@maraudersserver.com', '1234', result)
        iq = rpcresult
        
        self.assertEqual(iq.toXml(), "<iq to='moony@maraudersserver.com' type='result' id='1234' from='back.maraudersserver.com'><query xmlns='jabber:iq:rpc'><methodResponse><params><param><value><array><data><value><int>1</int></value><value><bool>1</bool></value><value><string>Lukas</string></value><value><struct><member><name>alter</name><value><int>7</int></value></member><member><name>groesse</name><value><double>1.450000</double></value></member></struct></value></data></array></value></param></params></methodResponse></query></iq>")
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()