#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from lxml import etree

import logging

logger = logging.getLogger('client')

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
            logger.error('Unable to read values.xml: %s' % str(e))
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
                # Remove list attrib from env var
                try:
                    del element.attrib["list"]
                except:
                    pass
                self.values[name] = etree.tostring(element)
            elif element.getchildren():
                self._parse(element, prefix=name)
            else:
                self.values[name] = element.text or ''
