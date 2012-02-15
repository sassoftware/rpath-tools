#
# Copyright (c) rPath, Inc.
#
from xml.etree import cElementTree as etree
from services import ServiceInfo
from services import ServiceScanner
from packages import PackageScanner
from packages import IDFactory

import time


class SurveyScanner(object):
    def __init__(self):
        self._serviceScanner = ServiceScanner(ServiceInfo)
        self._packageScanner = PackageScanner(IDFactory())

    def scan(self):
        services = self._serviceScanner.getServices()
        rpm_packages, conary_packages = self._packageScanner.scan()
        rpm_xml, conary_xml = self._packageScanner.toxml()
    
        rpm_packages_xml = etree.Element('rpm_packages')
        for result in rpm_xml:
            rpm_packages_xml.append(result)

        conary_packages_xml = etree.Element('conary_packages')
        for result in conary_xml:
            conary_packages_xml.append(result)

        services_xml = etree.Element('services')
        for srv in services:
            if srv.conary_pkg:
                troves = [ conary_packages.get(x) for x in srv.conary_pkg 
                            if x in conary_packages ]
                for trove in troves:
                    srv.conary_pkg_uri = self._packageScanner._idfactory.getId(
                                            trove)
            if srv.rpm_pkg:
                rpms = [ rpm_packages.get(x) for x in srv.rpm_pkg 
                            if x in rpm_packages]
                for rpm in rpms:
                    srv.rpm_pkg_uri = self._packageScanner._idfactory.getId(rpm)
            if srv.conary_pkg_uri:
                services_xml.append(srv.toxml(srv.conary_pkg_uri))
                continue
            if srv.rpm_pkg_uri:
                services_xml.append(srv.toxml(srv.rpm_pkg_uri))
                continue
            services_xml.append(srv.toxml(
                        self._packageScanner._idfactory.getId(srv)))

        return rpm_packages_xml, conary_packages_xml, services_xml

    def toxml(self):
        root = etree.Element('survey')
        etree.SubElement(root, 'created_date').text = str(int(time.time()))
        rpm_packages, conary_pkgs, services = self.scan()
        root.append(rpm_packages)
        root.append(conary_pkgs)
        root.append(services)
        return root

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

    scanner = SurveyScanner()
    dom = scanner.toxml()
    xml = etree.tostring(dom)
    print xml
