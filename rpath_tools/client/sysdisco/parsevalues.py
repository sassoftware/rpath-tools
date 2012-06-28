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
import collections

class ValuesParser(object):

    def __init__(self, values_xml):
        self.xml = self._root(values_xml)
        self.que =  collections.deque([])

    def _root(self, values_xml):
        tree = etree.ElementTree(file=values_xml)
        root = tree.getroot()
        return root

    def _parse(self, prefix, node):
        for element in node:
            name = "__".join([ prefix, element.tag ]).upper()
            if element.attrib and element.attrib["list"] == "true":
                self.que.append((name, etree.tostring(element)))
                continue
            if element.getchildren():
                self._parse(name, element)
                continue
            self.que.append((name, element.text))

    def parse(self):
        top_que = collections.deque([ (x.tag, x) for x in self.xml ])
        for prefix, node in top_que:
            self._parse(prefix, node)
        return dict(self.que)
