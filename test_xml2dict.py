#!/usr/bin/env python

"""
Unit tests for the xml2dict module. Designed to be used with `nose` for
running tests.

    $ nosetests --with-coverage --cover-package=xml2dict
"""

import unittest
import tempfile

from __init__ import xml2dict, dict2xml
from xml2dict import object_dict, XML2Dict


class TestObjectDict(unittest.TestCase):

    def test_object_dict(self):
        od = object_dict()
        od.fish = 'fish'
        self.assertEquals(od['fish'], 'fish')

    def test_object_dict_returns_value(self):
        od = object_dict()
        od.test = {'value': 1}
        self.assertEquals(od.test, 1)

    def test_object_dict_of_object_dict(self):
        od = object_dict()
        od.test = object_dict({'name': 'test_two', 'value': 2})
        self.assertEquals(od.test.name, 'test_two')
        self.assertEquals(od.test.value, 2)
        self.assertEquals(od.test, {'name': 'test_two', 'value': 2})


class TestXML2Dict(unittest.TestCase):

    def setUp(self):
        self.xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'

    def test_simple_xml_to_dict(self):
        xml = self.xml + '<a><b>5</b><c>9</c></a>'
        expected_output = {'a': {'b': '5', 'c': '9'}}
        self.assertEqual(xml2dict(xml), expected_output)

    def test_xml_to_list_of_values(self):
        xml = self.xml + '<a><b>1</b><b>2</b><b>3</b></a>'
        expected_output = {'a': {'b': ['1', '2', '3']}}
        self.assertEqual(xml2dict(xml), expected_output)

    def test_xml_to_mixture_of_lists_and_dicts(self):
        xml = self.xml + '<a><b>1</b><b>2</b><c><d>3</d></c></a>'
        expected_output = {'a': {'b': ['1', '2'], 'c': {'d': '3'}}}
        self.assertEqual(xml2dict(xml), expected_output)

    def test_xml_attributes_retained(self):
        xml = self.xml + '<numbers one="1" two="2" />'
        expected_output = {'numbers': {'one': '1', 'two': '2'}}
        self.assertEqual(xml2dict(xml), expected_output)

    def test_both_attributes_and_child_nodes(self):
        xml = self.xml + '<a foo="foo">bar</a>'
        expected_output = {'a': {'a': 'bar', 'foo': 'foo'}}
        self.assertEqual(xml2dict(xml), expected_output)

    def test_error_raised_when_passed_complicated_XML(self):
        xml = self.xml + '<tag tag="foo">bar</tag>'
        self.assertRaises(ValueError, xml2dict, xml)

    def test_against_XML_namespaces(self):
        namespaces_table = """
        <h:table xmlns:h="http://www.w3.org/TR/html4/">
          <h:tr>
           <h:td>Apples</h:td>
           <h:td>Bananas</h:td>
         </h:tr>
        </h:table>"""
        xml = self.xml + namespaces_table
        expected_output = {
            ('http://www.w3.org/TR/html4/', 'table'): {
                ('http://www.w3.org/TR/html4/', 'tr'): {
                    ('http://www.w3.org/TR/html4/', 'td'): ['Apples', 'Bananas']
                }
            }
        }
        self.assertEquals(xml2dict(xml), expected_output)

    def test_node_attribute_has_same_name_as_child(self):
        xml = self.xml + '<a b="foo"><b><c>1</c></b></a>'
        expected_output = {'a': {'b': ['foo', {'c': '1'}]}}
        self.assertEquals(xml2dict(xml), expected_output)

    def test_parsing_XML_from_file_from_function(self):
        xml = self.xml + '<a foo="bar" hello="word" />'
        f = tempfile.TemporaryFile(mode="w+t")
        f.write(xml)
        f.seek(0)
        expected_output = {'a': {'foo': 'bar', 'hello': 'word'}}
        self.assertEquals(xml2dict(f), expected_output)

    def test_parsing_XML_from_file_with_parse_method(self):
        xml = self.xml + '<a foo="bar" hello="word" />'
        f = tempfile.NamedTemporaryFile(mode="w+t")
        f.write(xml)
        f.seek(0)
        expected_output = {'a': {'foo': 'bar', 'hello': 'word'}}
        self.assertEquals(XML2Dict().parse(f.name), expected_output)


class TestDict2XML(unittest.TestCase):

    def setUp(self):
        self.xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'

    def test_dict2xml_fails_when_passed_a_list(self):
        self.assertRaises(TypeError, dict2xml, [])

    def test_dict2xml_fails_when_passed_more_than_one_root_node(self):
        my_dict = {'a': 1, 'b': 2}
        self.assertRaises(ValueError, dict2xml, my_dict)

    def test_dict2xml_fails_when_node_child_is_a_list(self):
        my_dict = {'a': [1, 2, 3]}
        self.assertRaises(ValueError, dict2xml, my_dict)

    def test_dict2xml_fails_when_passed_object_dictionary(self):
        self.assertRaises(ValueError, dict2xml, {'a': object()})

    def test_dict2xml_output_against_int_dictionary(self):
        my_dict = {1: 2}
        expected_xml = self.xml + '<1>2</1>'
        self.assertEquals(dict2xml(my_dict), expected_xml)

    def test_dict2xml_output_against_None_key(self):
        my_dict = {'a': None}
        expected_xml = self.xml + '<a />'
        self.assertEquals(dict2xml(my_dict), expected_xml)

    def test_dict2xml_output_against_child_list_of_None_values(self):
        my_dict = {'a': {'b': [None, None, None]}}
        expected_xml = self.xml + '<a><b /><b /><b /></a>'
        self.assertEquals(dict2xml(my_dict), expected_xml)

    def test_simple_dictionary_to_XML(self):
        my_dict = {'a': {'b': '5', 'c': '9'}}
        expected_xml = self.xml + '<a><c><![CDATA[9]]></c><b><![CDATA[5]]></b></a>'
        self.assertEquals(dict2xml(my_dict), expected_xml)

    def test_dictionary_with_list_to_XML(self):
        my_dict = {'a': {'b': ['1', '2', '3']}}
        expected_xml = self.xml + ('<a><b><![CDATA[1]]></b>'
                                   '<b><![CDATA[2]]></b>'
                                   '<b><![CDATA[3]]></b></a>')
        self.assertEqual(dict2xml(my_dict), expected_xml)

    def test_mixture_of_dictionaries_and_lists_to_XML(self):
        my_dict = {'a': {'b': ['1', '2'], 'c': {'d': '3'}}}
        expected_xml = self.xml + ('<a><c><d><![CDATA[3]]></d></c>'
                                   '<b><![CDATA[1]]></b><b><![CDATA[2]]></b>'
                                   '</a>')
        self.assertEquals(dict2xml(my_dict), expected_xml)
