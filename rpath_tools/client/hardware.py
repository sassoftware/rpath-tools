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


import socket
import struct
from conary.lib import util
from rpath_tools.client import utils
from rpath_tools.lib import netlink


class HardwareData(object):

    class IP(object):
        __slots__ = ['ipv4', 'ipv6', 'device', 'netmask', 'dns_name']
        def __init__(self, *args, **kwargs):
            for k in self.__slots__:
                setattr(self, k, kwargs.get(k, None))

    def __init__(self, cfg):
        self.ips = []
        self.deviceName = ''

    def getIpAddresses(self):
        if self.ips:
            return self.ips
        rnl = netlink.RoutingNetlink()
        for iface, addrs in rnl.getAllAddresses().items():
            for family, address, prefix in addrs:
                if family != 'inet':
                    continue
                netmask = ((1 << prefix) - 1) << (32 - prefix)
                netmask = socket.inet_ntop(socket.AF_INET,
                        struct.pack('>I', netmask))
                self.ips.append(self.IP(
                    ipv4=address,
                    netmask=netmask,
                    device=iface,
                    dnsname=self.resolve(address) or address,
                    ))

        if utils.runningInEC2():
            self.ips.append(self._getExternalEC2Network())

        return self.ips

    def resolve(self, ipaddr):
        try:
            info = socket.gethostbyaddr(ipaddr)
            return info[0]
        except (socket.herror, socket.gaierror):
            return None

    def getHostname(self):
        return socket.gethostname()

    def getLocalIp(self, ipList):
        if ipList:
            return self._getLocalIp(ipList[0])
        # Hope for the best
        return self._getLocalIp('8.8.8.8')

    def getDeviceName(self, localIp):
        if self.deviceName:
            return self.deviceName
        else:
            ips = self.getIpAddresses()
            for ip in ips:
                active = (ip.ipv4 == localIp)
                if active:
                    self.deviceName = ip.device
                    return self.deviceName

    @classmethod
    def _getLocalIp(cls, destination):
        """Return my IP address visible to the destination host"""

        if utils.runningInEC2():
            return cls._getExternalEC2Ip()

        if "://" not in destination:
            destination = "http://%s" % destination
        hostname, port = util.urlSplit(destination, defaultPort=443)[3:5]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((hostname, int(port)))
        ret = s.getsockname()[0]
        s.close()
        return ret

    @classmethod
    def _getExternalEC2Ip(cls):
        try:
            from amiconfig import instancedata
            instanceData = instancedata.InstanceData()
        except ImportError:
            return

        return instanceData.getPublicIPv4()

    def _getExternalEC2Network(self):
        try:
            from amiconfig import instancedata
            instanceData = instancedata.InstanceData()
        except ImportError:
            return

        return self.IP(
            ipv4=instanceData.getPublicIPv4(),
            netmask='255.255.255.0',
            device='eth0-ec2',
            dns_name=instanceData.getPublicHostname())
