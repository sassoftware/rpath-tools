#!/usr/conary/bin/python2.6
#
# Copyright (C) 2010 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

import xml.etree.cElementTree as etree

class ValuesParserError(Exception):
    "Raised when unable to read values.xml"

class ValuesParser(object):

    def __init__(self, values_xml):
        self.xml = self._root(values_xml)
        self.values = {}

    def _root(self, values_xml):
        try:
            tree = etree.ElementTree(file=values_xml)
        except Exception, e:
            raise ValuesParserError, e
        root = tree.getroot()
        return root

    def parse(self):
        self.values = {}
        self._parse(self.xml, prefix=None)
        return self.values

    def _parse(self, node, prefix):
        for element in node:
            name = element.tag.upper()
            if prefix:
                name = prefix + '__' + name

            if element.attrib and element.attrib["list"] == "true":
                self.values[name] = etree.tostring(element)
            elif element.getchildren():
                self._parse(element, prefix=name)
            else:
                self.values[name] = element.text or ''
