#
# Copyright (c) 2012 rPath, Inc.
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

import os
import sys

import xml.etree.cElementTree as etree

from collections import namedtuple

from conary.lib import util

import executioner
import parsevalues

valuesXmlPath = "/var/lib/rpath-tools/values.xml"
readExtensionPath = "/usr/lib/rpath-tools/read.d/"
writeExtensionPath = "/usr/lib/rpath-tools/write.d/"
discoverExtensionPath = "/usr/lib/rpath-tools/discover.d"
validateExtensionPath = "/usr/lib/rpath-tools/validate.d"


class CONFIGURATOR(namedtuple('configurator' , 'name extpath vxml')):
        __slots__ = ()

class RunConfigurators(object):

    def __init__(self):
        read = CONFIGURATOR('observed_values', readExtensionPath, 
                                    valuesXmlPath)
        validate = CONFIGURATOR('validation_report', validateExtensionPath,
                                        valuesXmlPath)
        discover = CONFIGURATOR('discovered_values', discoverExtensionPath,
                                        valuesXmlPath)

        self.configurators = [ read, validate, discover ]

    def _run(self, configurator):
        executer = executioner.Executioner(configurator.extpath, configurator.vxml)
        xml = executer.toxml()
        return xml

    def _toxml(self, configurator):
        configurator_xml = self._run(configurator)
        xml = etree.Element(configurator.name)
        errors_xml = etree.SubElement(xml, 'errors')
        extensions_xml = etree.SubElement(xml, 'extensions')
        nodes = configurator_xml.getchildren()
        for node in nodes:
            errors = node.find('errors')
            for child in errors.getchildren():
                errors_xml.append(child)
            extensions = node.find('extensions')
            for child in extensions.getchildren():
                extensions_xml.append(child)
            #TODO add total success status?
            #success = node.find('success')
            #if success:
            #    xml.append(success)
        return xml

    def toxml(self):
        root = etree.Element('configurators')
        for configurator in self.configurators:
            root.append(self._toxml(configurator))
        return root

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    configurators = RunConfigurators()
    root = configurators.toxml()
    print(etree.tostring(root))

