#
# Copyright (c) rPath, Inc.
#

from collections import namedtuple
from xml.etree import cElementTree as etree

import os
import socket
import platform


class LinuxInfo(object):
    def __init__():
        self.platform = None
        self.hostname = None
        self.kernel = None 
        self.build = None
        self.arch = None
        self.processor = None
        self.ifaces = None
        self.distribution = None
        self.architecture = None
        self.runlevel = None
        self.rpm = None

    def _getifaces(self):
        ifaces = { 'eth0' : [ ('192.168.11.1', '00:50:56:B4:06:8B') ]
        return ifaces

    def _getinfo(self):
        self.platform, self.hostname, self.kernel, self.build, self.arch, self.processor = platform.uname()      
        self.ifaces = self._getifaces()
        self.distribution = platform.linux_distribution()
        self.architecture = platform.architecture()

    def toxml(self):
        self._getinfo()
        root = etree.Element('sysinfo')

class SysInfo(object):    
    def __init__(self, name, uuid, ctime):
        self.linux = LinuxInfo()
        self.windows = WindowsInfo()
        self.name = name
        self.hostname = None
        self.uuid = uuid
        self.uid = None
        self.gid = None
        self.ctime = ctime
        self.status = status
        self.conary = None


    def getinfo(self):
        if platform.system() == 'Linux':
            sysInfo = self.linux.toxml()
        elif platform.system() == 'Windows':
            sysInfo = self.windows.toxml()
        return sysInfo




