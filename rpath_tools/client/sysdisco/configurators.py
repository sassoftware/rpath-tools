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


import os
import uuid
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
writeErrorTemplate = os.path.join(templatePath, "write_error_template.xml")
readErrorTemplate = os.path.join(templatePath, "read_error_template.xml")
validateErrorTemplate = os.path.join(templatePath, "validation_error_template.xml")
discoverErrorTemplate = os.path.join(templatePath, "discover_error_template.xml")


class CONFIGURATOR(BaseSlots):
    __slots__ = [ 'name', 'extpath', 'vxml', 'errtmpl', 
                    'error', 'retval', 'retcode', 'xml' ]
    def __repr__(self):
        return '%s' % self.name
    def description(self):
        return ( "Name = %s\nExtension Path = %s\nValues XML= %s\n" 
                "Error Template = %s\nError = %s\nRETVAL = %s\n"
                "RETCODE = %S\nXML = %s\n" %
                ('name', 'extpath', 'vxml', 'errtmpl', 
                    'error', 'retval', 'retcode', 'xml'))



class RunConfigurators(object):

    def __init__(self, configurators=None):

        write = CONFIGURATOR(name='write_reports', 
                            extpath=writeExtensionPath,
                            vxml=valuesXmlPath, 
                            errtmpl=writeErrorTemplate
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


        self.runConfigurators = os.path.exists(valuesXmlPath)

        self.configurators = []

        if configurators:
            for configurator in configurators:
                self.configurators.append(self.configurator_types[configurator])

        if not self.configurators:
            self.configurators = [ read, validate, discover ]

        self.xsdattrib = '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'

    def _sanitize(self, results):
        from xml.sax.saxutils import escape
        return escape(results)

    def _plateXml(self, result):
        # XML Template for when no configurator exists
        # If we have errors switch templates
        if result.retval:
            return self._errorXml(result)
        plate_xml = etree.Element(result.name)
        template = etree.parse(result.errtmpl).getroot()
        # Get the xsd info from the error templates...ugly I know
        plate_node = etree.SubElement(plate_xml, template.tag, template.attrib)
        etree.SubElement(plate_node, 'name').text = result.name
        # Make sure the xslt likes what it sees
        etree.SubElement(plate_node, 'success').text = 'true'
        retval, p_xml, retcode = self._transform(plate_xml)
        return etree.fromstring(p_xml)

    def _errorXml(self, result):
        error_xml = etree.Element(result.name)
        error_name = 'config_error-%s' % uuid.uuid1()
        template = open(result.errtmpl).read()
        template = template.replace('__name__',error_name)
        template = template.replace('__display_name__',result.name)
        template = template.replace('__summary__','%s type configurator' % result.name)
        template = template.replace('__details__',self._sanitize(str(result.error)))
        template = template.replace('__error_code__','999')
        template = template.replace('__error_details__','xslt transform error')
        template = template.replace('__error_summary__','Invalid XML')
        error_xml.append(etree.fromstring(template))
        retval, err_xml, retcode = self._transform(error_xml)
        return etree.fromstring(err_xml)


    def _run(self, configurator):
        # TODO < FIXME
        # Change this and pass the whole configurator to it...
        executer = Executioner(configurator.name,
                                configurator.extpath,
                                configurator.vxml,
                                configurator.errtmpl)
        xml = executer.toxml()
        return xml


    def _transform(self, xml):
        # place holder have to look up the right way
        xslname = 'rpath-configurator-2.0.xsl'
        # get this from the url in the xml if possible
        xsds = [ node.attrib[self.xsdattrib].split()[-1]
                    for node in xml.getchildren() ]
        if len(xsds):
            xsd = xsds[0]
            xslname = xsd.replace('.xsd', '.xsl')
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
        # output should be xml from the configurator
        output = self._run(configurator)
        if output is not None:
            configurator.retval, configurator.xml, configurator.retcode = self._transform(output)
            if configurator.retval:
                return etree.fromstring(configurator.xml)
            else:
                configurator.error = output
        return self._plateXml(configurator)

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
