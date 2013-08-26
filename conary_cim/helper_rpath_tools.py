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


import logging
import os
from conary.lib import networking
from conary.lib.http import request

from rpath_tools.client import register
from rpath_tools.client import command
from rpath_tools.client import config
from rpath_tools.client import hardware
from rpath_tools.client import main

logger = logging.getLogger('rpath_tools')

class Registration(object):
    CONFIG_D_DIRECTORY = "config.d"

    def __init__(self, configFile=None, event_uuid=None):
        self.event_uuid = event_uuid
        self.cfg = config.RpathToolsConfiguration(readConfigFiles = True)
        if configFile is not None:
            self.cfg.read(configFile)

        self.hwData = hardware.HardwareData(self.cfg)
        self.registration = register.Registration(self.cfg)
        remote = self.registration.getRemote()
        localIp = self.hwData.getLocalIp(remote)
        deviceName = self.hwData.getDeviceName(localIp)
        self.registration.setDeviceName(deviceName)

    def reset(self):
        self.cfg.configLine("includeConfigFile %s/%s/*" % (self.cfg.topDir,
            self.CONFIG_D_DIRECTORY))

    @property
    def generatedUuid(self):
        return self.registration.generatedUuid

    @property
    def localUuid(self):
        return self.registration.localUuid

    def setManagementNodes(self, managementNodes):
        configFilePath = os.path.join(self.cfg.topDir, self.CONFIG_D_DIRECTORY, "directMethod")
        f = file(configFilePath, "w")
        f.write("directMethod []\n")
        for n in managementNodes:
            f.write("directMethod %s\n" % n)
        f.close()

    def setConaryProxy(self, managementNodes):
        proxies = set()
        for remote in managementNodes:
            if not remote.strip():
                continue
            # Strip off port in a way that works for IPv4 and IPv6
            # 1.2.3.4:8443 -> conarys://1.2.3.4
            # [fd00::1234]:8443 -> conarys://[fd00::1234]
            try:
                host = networking.HostPort(remote).host
            except ValueError:
                continue
            hostport = networking.HostPort(host, None)
            url = request.URL(
                    scheme='conarys',
                    userpass=(None, None),
                    hostport=hostport,
                    path='',
                    )
            proxies.add(str(url))
        if not proxies:
            return
        with open(self.cfg.conaryProxyFilePath, 'w') as f:
            print >> f, 'proxyMap *', ' '.join(sorted(proxies))

    def setRequiredNetwork(self, requiredNetwork):
        configFilePath = os.path.join(self.cfg.topDir, self.CONFIG_D_DIRECTORY, "requiredNetwork")
        if requiredNetwork is None:
            if os.path.exists(configFilePath):
                os.unlink(configFilePath)
            return
        f = file(configFilePath, "w")
        f.write("requiredNetwork %s\n" % requiredNetwork)
        f.close()

    def run(self, event_uuid=None):
        m = main.RpathToolsMain()
        cmd = command.RegistrationCommand()
        return m.runCommand(cmd, self.cfg,
            {'force' : False, 'event-uuid' : self.event_uuid}, ())
