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

import traceback

from lxml import etree

from conary.lib import util

from executioner import Executioner

from executioner import BaseSlots

# CONFIG VARIABLES
valuesXmlPath = "/var/lib/rpath-tools/values.xml"
readExtensionPath = "/usr/lib/rpath-tools/read.d/"
writeExtensionPath = "/usr/lib/rpath-tools/write.d/"
discoverExtensionPath = "/usr/lib/rpath-tools/discover.d"
validateExtensionPath = "/usr/lib/rpath-tools/validate.d"
xslFilePath = "/usr/conary/share/rpath-tools/xml_resources/xsl"
templatePath = "/usr/conary/share/rpath-tools/xml_resources/templates"
readErrorTemplate = os.path.join(templatePath, "read_error_template.xml")
validateErrorTemplate = os.path.join(templatePath, "validation_error_template.xml")
discoverErrorTemplate = os.path.join(templatePath, "discover_error_template.xml")


class CONFIGURATOR(BaseSlots):
    __slots__ = [ 'name', 'extpath', 'vxml', 'errtmpl', 'error', 'xml' ]
    def __repr__(self):
        return '%s' % self.name
    def description(self):
        return ( "Name = %s\nExtension Path = %s\nValues XML= %s\n Error Template = %s\nError = %s\n"
                "XML = %s\n" %
                ('name', 'extpath', 'vxml', 'errtmpl', 'error', 'xml'))



class RunConfigurators(object):

    def __init__(self, configurators=None):
        write = CONFIGURATOR(name='write', 
                            extpath=writeExtensionPath,
                            vxml=valuesXmlPath, 
                            errtmpl=''
                            )
        read = CONFIGURATOR(name='read_reports', 
                            extpath=readExtensionPath, 
                            vxml=valuesXmlPath, 
                            errtmpl=readErrorTemplate
                            )
        validate = CONFIGURATOR(name='validation_reports', 
                            extpath=validateExtensionPath,
                            vxml=valuesXmlPath, 
                            errtmpl=validateErrorTemplate
                            )
        discover = CONFIGURATOR(name='discovery_reports', 
                            extpath=discoverExtensionPath,
                            vxml=valuesXmlPath, 
                            errtmpl=discoverErrorTemplate
                            )

        self.configurator_types = dict([('read', read),('validate', validate),
                                        ('discover', discover), 
                                        ('write', write)])

        self.configurators = []

        if configurators:
            for configurator in configurators:
                self.configurators.append(self.configurator_types[configurator])

        if not self.configurators:
            self.configurators = [ read, validate, discover ]


    def _errorXml(self, result):
        error_xml = etree.element(result.name)
        error_name = 'config_error-%s' % uuid.uuid1()
        template = open(result.errtmpl).read()
        template = template.replace('__name__',error_name)
        template = template.replace('__display_name__',result.name)
        template = template.replace('__summary__','%s type configurator' % result.name)
        template = template.replace('__details__',str(result.error))
        template = template.replace('__error_code__','999')
        template = template.replace('__error_details__','xslt transform error')
        template = template.replace('__error_summary__','this is bad...')
        error_xml.append(etree.fromstring(template))
        return error_xml


    def _run(self, configurator):
        # TODO < FIXME
        # Change this and pass the whole configurator to it...or just add the name
        #executer = executioner.Executioner(configurator.extpath, configurator.vxml)
        executer = Executioner(configurator.name, 
                                configurator.extpath, 
                                configurator.vxml, 
                                configurator.errtmpl)
        xml = executer.toxml()
        return xml


    def _transform(self, xml):
        # place holder have to look up the right way 
        # get this from the url in the xml not this way
        xslname = 'rpath-configurator-2.0.xsl'
        version = [ node.attrib['version'] for node in xml.getchildren() ]
        # probably need to deal with 2 vs 2.0
        if version:
            ver = float(version[0])
            xslname = 'rpath-configurator-%.1f.xsl' % ver
        xslFile = os.path.join(xslFilePath,  xslname)
        xslt_doc = etree.parse(xslFile)
        transformer = etree.XSLT(xslt_doc)
        try:
            xs = transformer(xml)
        except etree.XSLTApplyError, ex:
            msg = "%s\n"  % str(ex.error_log)
            msg += traceback.format_exc()
            return False, msg, 70
        return True, str(xs), 0


    def _toxml(self, configurator):
        configurator_xml = self._run(configurator)
        retval, configurator.xml, retcode = self._transform(configurator_xml)
        # TODO
        # if retval shit should go bad
        # wrap all up in clean xml??a
        if retval:
            return etree.fromstring(configurator.xml)
        #from conary.lib import epdb;epdb.st()
        return self._errorXml(configurator)

    def toxml(self):
        root = etree.Element('configurators')
        for configurator in self.configurators:
            root.append(self._toxml(configurator))
        return root

if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()
    configurators = RunConfigurators()
    root = configurators.toxml()
    print(etree.tostring(root))

