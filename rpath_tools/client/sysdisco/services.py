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

import os
import subprocess

import rpm

from conary import conarycfg
from conary import conaryclient
from conary.cmds import query


from packages import RPMInfo
from packages import ConaryInfo

# ServiceInfo has to be mutable

class ServiceInfo(object):
    def __init__(self, name, status, autostart, runlevels):
        self.name = name
        self.status = status
        self.autostart = autostart
        self.runlevels = runlevels
        self.init = os.path.join(os.path.realpath('/etc/init.d'),self.name).encode('ascii')
        self.running = self._checkRunning()
        self.conary_pkg = None
        self.rpm_pkg = None
        self.conary_pkg_uri = None
        self.rpm_pkg_uri = None

    def _checkRunning(self):
        running = 'false'
        if 'not running' in self.status or 'dead' in self.status:
            running = 'false'
        elif 'running' in self.status or 'pid' in self.status:
            running = 'true'
        elif 'ACCEPT' in self.status:
            running = 'true'
        return running

    def toxml(self, srv_id):
        root = etree.Element('service', id=srv_id)
        childStatus = etree.SubElement(root, 'status').text = self.status 
        childRunning = etree.SubElement(root, 'running').text = self.running
        childServiceInfo = etree.SubElement(root, 'service_info' )
        childName = etree.SubElement(childServiceInfo, 'name' ).text = self.name
        childAutostart = etree.SubElement(childServiceInfo, 'autostart').text = self.autostart
        childRunlevels = etree.SubElement(childServiceInfo, 'runlevels')
        rls = []
        for rl in sorted(self.runlevels):
            if self.runlevels[rl] == 'on':
                rls.append(rl )
        childRunlevels.text = ",".join(sorted(rls))     
        #if self.rpm_pkg:
        #    childRpmPkg.text = self.rpm_pkg.nevra
        #if self.conary_pkg:
        #    childConaryPkg.text = self.conary_pkg
        if self.rpm_pkg_uri:
            childRpmPkg = etree.SubElement(root, 'rpm_package', 
                                            dict(id=self.rpm_pkg_uri))
        else:
            childRpmPkg = etree.SubElement(root, 'rpm_package')

        if self.conary_pkg_uri:
            childConaryPkg =  etree.SubElement(root, 'conary_package', 
                                            dict(id=self.conary_pkg_uri))
        else:
            childConaryPkg = etree.SubElement(root, 'conary_package')

        return root

class ServiceScanner(object):
    def __init__(self, ServiceInfo):
        self.services = []
        self.servicesSet = set()
        self._serviceInfo = ServiceInfo


    def _runProcess(self, cmd):
        '''cmd @ [ '/sbin/service', 'name', 'status' ]'''
        try:
            proc = subprocess.Popen(cmd, shell=False, stdin=None, 
                        stdout=subprocess.PIPE , stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            #if proc.returncode != 0:
                # TODO: Fix results up"
                #raise Exception("%s failed with return code %s" % (' '.join(cmd), proc.returncode))
                #return stderr.decode("UTF8")
            return stdout.decode("UTF8")
        except Exception, ex:
            return ex


    def _getRunlevel(self):
        if os.path.exists('/sbin/runlevel'):
            rl_cmd = [ '/sbin/runlevel' ]
        elif os.path.exists('/usr/bin/who'):
            rl_cmd = [ '/sbin/who' , '-r' ]
        else:
            pass
        if rl_cmd:
            stdout = self._runProcess(rl_cmd)
            current_runlevel = stdout.split()[-1]
        else:
            current_runlevel = 'unknown'
        return current_runlevel

    def _getServices(self):
        chkconfig = [ '/sbin/chkconfig' , '--list' ]
        services = [ ['chkconfig_missing', '0:off', 
                        '1:off', '2:off', '3:off', '4:off', '5:off', '6:off'] ]
        if os.path.exists(chkconfig[0]):
            stdout = self._runProcess(chkconfig)
            services = [ [ y for y in x.split() ] for x in  stdout.split('\n') 
                            if x and 'xinetd' not in x ]
        return services

    def _getRpm(self, init_script):
        try:
            ts = rpm.TransactionSet()
            mi = ts.dbMatch()
            hdrs = [ RPMInfo.fromHeader(h) for h in mi if init_script in h['filenames'] ]
            _results = dict((h.nevra, h) for h in hdrs)
        except:
            _results = {}

        return _results

    def _getConaryPkg(self, init_script):
        conary_list = []
        trv = ([], False)
        cfg = conarycfg.ConaryConfiguration(True)
        cli = conaryclient.ConaryClient(cfg)
        db = cli.db
        trv = query.getTrovesToDisplay(db, troveSpecs=[], pathList=[init_script])
        if trv[0]:
            conary_list.append(trv[0][0])
        return conary_list



    def _fromString(self, cls, srv):
        self.current_runlevel = self._getRunlevel()
        autostart = 'false'
        status = 'off'
        name = srv[0]
        if name.endswith(':'):
            name = name.strip(':')
        service = [ '/sbin/service', name, 'status' ]
        status = self._runProcess(service)
        if len(srv[1:]) == 1:
            runlevels = {'xinetd' : srv[1:][0]}
            status = '''run in xinetd... %s''' % srv[1:][0]
        elif len(srv[1:]) >= 6:
            runlevels = dict((z.split(':')) for z in srv[1:]) 
        if ( self.current_runlevel in runlevels 
                and runlevels[self.current_runlevel] == 'on' ):
            autostart = 'true'
        return cls(name, status, autostart, runlevels)

    def getServices(self):
        self.services = self._getServices()
        for srv in self.services:
            srvObj = self._fromString(self._serviceInfo, srv)
            rpms = self._getRpm(srvObj.init)
            if rpms:
                srvObj.rpm_pkg = rpms
            conary_pkgs =  self._getConaryPkg(srvObj.init)
            if conary_pkgs:
                srvObj.conary_pkg = conary_pkgs
            self.servicesSet.add(srvObj)
        return self.servicesSet

    def toxml(self):
        if not self.servicesSet:
            self.getServices()
        roottag = "services"
        root = etree.Element(roottag)
        srv_id = 0
        for srv in self.servicesSet:
            root.append(srv.toxml(str(srv_id)))
            srv_id += 1
        return root


if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    services = ServiceScanner(ServiceInfo)
    xml = services.toxml()
    print(etree.tostring(xml))
