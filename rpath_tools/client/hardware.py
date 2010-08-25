#
# Copyright (c) 2010 rPath, Inc.
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


import socket
from conary.lib import util
from rpath_tools.client.utils import wbemlib

class WBEMData(object):
    
    cimClasses = []

    def __init__(self, url=None):
        self.url = url or '/tmp/sfcbHttpSocket'
        self.server = wbemlib.WBEMServer(self.url)
        self.data = {}
    
    def populate(self):
        for cimClassDict in self.cimClasses:
            for cimClass, cimProperties in cimClassDict.items():
                self.data[cimClass] = {}
                insts = getattr(self.server, cimClass).EnumerateInstances()
                for inst in insts:
                    instId = inst.properties['instanceID'].value
                    if not instId:
                        instId = inst.properties['Name'].value
                    self.data[cimClass][instId] = {} 
                    for cimProperty in cimProperties:
                        self.data[cimClass][instId][cimProperty] = \
                            inst.properties[cimProperty].value

    def getData(self):
        return self.data


class HardwareData(WBEMData):
    
    cimSystemClasses = {'Linux_OperatingSystem' : ['ElementName',
                            'OSType', 'Version']}
    cimCpuClasses = {'Linux_Processor' : ['ElementName',
                            'NumberOfEnabledCores', 'MaxClockSpeed']}
    cimNetworkClasses = {'Linux_IPProtocolEndpoint' : [
                            'IPv4Address', 'IPv6Address',
                            'SubnetMask', 'ProtocolType', 'SystemName',
                            'Name', 'NameFormat',
                            ]}

    cimClasses = [cimNetworkClasses]

    class IP(object):
        __slots__ = ['ipv4', 'ipv6', 'device', 'netmask', 'dns_name']
        def __init__(self, *args, **kwargs):
            for k in self.__slots__:
                setattr(self, k, kwargs.get(k, None))

    @property
    def hardware(self):
        self.populate()
        return self.getData()

    def getIpAddresses(self):
        ips = []
        for iface in self.hardware['Linux_IPProtocolEndpoint'].values():
            ipv4 = iface['IPv4Address']
            if ipv4 is not None and  ipv4 not in ('NULL', '127.0.0.1'):
                device = iface['Name']
                device = device.split('_')
                if len(device) > 1:
                    deviceName = device[1]
                else:
                    deviceName = device[0]
                dnsName = self.resolve(ipv4) or ipv4
                ip = self.IP(ipv4=ipv4, netmask=iface['SubnetMask'],
                    device=deviceName, dns_name=dnsName)
                ips.append(ip)
        return ips

    def resolve(self, ipaddr):
        try:
            info = socket.gethostbyaddr(ipaddr)
            return info[0]
        except (socket.herror, socket.gaierror):
            return None

    def getHostname(self):
        hostname = "/bin/hostname"
        cmd = [ hostname ]
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        sts = p.wait()
        if sts != 0:
            raise Exception("Unable to read hostname")
        hostname = p.stdout.readline().strip()
        return hostname

    def getLocalIp(self, ipList):
        if ipList:
            return self._getLocalIp(ipList[0])
        # Hope for the best
        return self._getLocalIp('8.8.8.8')

    @classmethod
    def _getLocalIp(cls, destination):
        """Return my IP address visible to the destination host"""
        if "://" not in destination:
            destination = "http://%s" % destination
        hostname, port = util.urlSplit(destination, defaultPort=443)[3:5]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((hostname, int(port)))
        ret = s.getsockname()[0]
        s.close()
        return ret

def main(url=None):
    h = HardwareData(url)
    return h.hardware

if __name__ == '__main__':
    hwData = main()
    print hwData
