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

from services import ServiceInfo
from services import ServiceScanner
from packages import PackageScanner
from packages import IDFactory
from configurators import RunConfigurators
from configurators import valuesXmlPath
from preview import Preview
from descriptors import Descriptors

import sys 
import time
import os
import uuid

import logging

logger = logging.getLogger('client')

class SurveyScanner(object):
    def __init__(self, origin="scanner"):
        self._serviceScanner = ServiceScanner(ServiceInfo)
        self._packageScanner = PackageScanner(IDFactory())
        self.origin = origin
        self.uuid = None

    def _getServices(self):
        return self._serviceScanner.getServices()

    def _getPackages(self):
        return self._packageScanner.scan()

    def getServicesXML(self):
        services = self._getServices()
        rpm_pkgs, conary_pkgs = self._getPackages()
        services_xml = etree.Element('services')
        srv_id = 100
        for srv in services:
            if srv.conary_pkg:
                troves = [ conary_pkgs.get(x) for x in srv.conary_pkg 
                            if x in conary_pkgs ]
                for trove in troves:
                    srv.conary_pkg_uri = self._packageScanner._idfactory.getId(
                                            trove)
            if srv.rpm_pkg:
                rpms = [ rpm_pkgs.get(x) for x in srv.rpm_pkg 
                            if x in rpm_pkgs]
                for rpm in rpms:
                    srv.rpm_pkg_uri = self._packageScanner._idfactory.getId(rpm)
            services_xml.append(srv.toxml(str(srv_id)))
            srv_id += 1
        return services_xml

    def getPackagesXML(self):
        rpm_xml, conary_xml = self._packageScanner.toxml()
        rpm_pkgs_xml = etree.Element('rpm_packages')
        for result in rpm_xml:
            rpm_pkgs_xml.append(result)
        conary_pkgs_xml = etree.Element('conary_packages')
        for result in conary_xml:
            conary_pkgs_xml.append(result)
        return rpm_pkgs_xml, conary_pkgs_xml

    def getSystemModelXML(self):
        sysmod_xml = etree.Element('system_model')
        systemModel = self._packageScanner.getSystemModel()
        if systemModel:
            sysmod_xml = systemModel.toxml()
        return sysmod_xml

    def getValuesXML(self):
        values_xml = etree.Element('config_properties')
        if os.path.exists(valuesXmlPath):
            values_xml.append(etree.parse(valuesXmlPath).getroot())
        return values_xml

    def getPreviewXML(self, sources=None):
        # Preview returns an empty preview tag if it fails
        preview = Preview()
        raw_preview_xml = preview.preview(sources)
        if raw_preview_xml:
            try:
                preview_xml = etree.fromstring(raw_preview_xml)
            except SyntaxError, ex:
                # FIX ME This is going to  go bad at some point
                logger.error('Error with xml from preview:\n %s' % str(ex)) 
                pass
        return preview_xml

    def getConfigurators(self):
        # Adds observed_values, discovered_values, and validation_report
        # from configurators.
        configurators = RunConfigurators()
        configurators_xml = configurators.toxml()
        configurator_nodes = []
        for node in configurators_xml.getchildren():
            configurator_nodes.append(node)
        return configurator_nodes

    def getDescriptors(self):
        descriptors_xml = etree.Element('config_properties_descriptor')
        descriptors = Descriptors()
        raw_desc = descriptors.toxml()
        if raw_desc:
            # FIXME UGLY... have to remove the xsd 
            # from the configuration_descriptor 
            # so that we don't get them later. 
            # I know there is an easier fix just 
            # need to think about it.
            rep = [ x for x in raw_desc.split('\n') 
                    if x.startswith('<configuration_descriptor')][0]
            try:
                descriptors_namespace_fix = etree.fromstring(
                    raw_desc.replace(rep, '<configuration_descriptor>'))
                descriptors_xml.append(descriptors_namespace_fix)
            except SyntaxError, ex:
                logger.error('Error with xml from descriptors:\n %s' % str(ex))
                pass
            # END FIXME
        return descriptors_xml

    def scan(self, sources=None):
        self.uuid = uuid.uuid4()
        self.sources = []
        if sources:
            self.sources = sources
        preview_xml = self.getPreviewXML(self.sources)
        rpm_xml, conary_xml = self.getPackagesXML()
        services_xml = self.getServicesXML()
        values_xml = self.getValuesXML()
        descriptors_xml = self.getDescriptors()
        configurator_nodes = self.getConfigurators()
        return rpm_xml, conary_xml, services_xml, values_xml, preview_xml, configurator_nodes, descriptors_xml

    def toxml(self, sources=None):
        # Scan first. This will create the new uuid
        rpm_pkgs, conary_pkgs, services, values, preview, configurators, descriptors = self.scan(sources)
        root = etree.Element('survey')
        etree.SubElement(root, 'uuid').text = str(self.uuid)
        etree.SubElement(root, 'created_date').text = str(int(time.time()))
        sysmodel = self._packageScanner.getSystemModel()
        if sysmodel is not None:
            root.append(sysmodel.toxml())
        root.append(rpm_pkgs)
        root.append(conary_pkgs)
        root.append(services)
        root.append(values)
        etree.SubElement(root, 'origin').text = str(self.origin)
        root.append(preview)
        root.append(descriptors)
        for node in configurators:
            root.append(node)
        return root

if __name__ == '__main__':
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    scanner = SurveyScanner()
    sources = [ 'group-smitty-c6e-goad-appliance=/smitty-c6e-goad.eng.rpath.com@rpath:smitty-c6e-goad-1-devel/1-63-1' ]
    dom = scanner.toxml(sources)
    xml = etree.tostring(dom)
    print xml
