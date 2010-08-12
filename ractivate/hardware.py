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


from ractivate.utils import wbemlib

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
    cimNetworkClasses = {'Linux_IPProtocolEndpoint' : ['IPv4Address',
                            'SubnetMask', 'ProtocolType', 'SystemName']}

    cimClasses = [cimNetworkClasses]

    @property
    def hardware(self):
        self.populate()
        return self.getData()

    def getIpAddr(self):
        ips = []
        for iface in self.hardware['Linux_IPProtocolEndpoint'].values():
            ip = iface['IPv4Address']
            if ip is not None and ip not in ('NULL', '127.0.0.1'):
                ips.append(ip)

        # TODO: handle multiple ip's
        return ips[0]

    def getHostname(self):
        hostnames = [i['SystemName'] for i \
            in self.hardware['Linux_IPProtocolEndpoint'].values()] 
        for hostname in hostnames:
            if hostname != 'localhost.localdomain':
                return hostname
        if hostnames:
            return hostnames[0]

        return None

def main(url=None):
    h = HardwareData(url)
    return h.hardware

if __name__ == '__main__':
    hwData = main()
    print hwData
