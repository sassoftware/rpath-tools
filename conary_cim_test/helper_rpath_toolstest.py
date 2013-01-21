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
import sys

from conary.lib import util

import testbase

class HelperRpathToolsTest(testbase.TestCase):
    def testSetManagementNodes(self):
        tmpPath = self.workDir + '/temp'
        configD = self.workDir + '/config.d'
        util.mkdirChain(tmpPath)
        util.mkdirChain(configD)
        rPathToolsPath = os.path.join(tmpPath, "rpath_tools")
        util.mkdirChain(tmpPath, rPathToolsPath)

        file(os.path.join(rPathToolsPath, "__init__.py"), "w").write("")
        file(os.path.join(rPathToolsPath, "client.py"), "w").write("""
class register(object):
    class Registration(object):
        def __init__(self, *args, **kwargs):
            pass
        def getRemote(slf):
            return 'blah'
        def setDeviceName(slf, deviceName):
            return 'eth0'

class hardware(object):
    class HardwareData(object):
        def __init__(self, *args, **kwargs):
            pass
        def getDeviceName(self):
            pass
        def getLocalIp(slf, remote):
            return '1.2.3.4'
        def getDeviceName(slf, localIp):
            return 'eth0'

class command(object):
    pass

class config(object):
    class RpathToolsConfiguration(object):
        def __init__(self, *args, **kwargs):
            pass

class main(object):
    pass
""")
        try:
            sys.path.append(tmpPath)
            import helper_rpath_tools
            class Registration(helper_rpath_tools.Registration):
                CONFIG_D_DIRECTORY = configD

            registration = Registration()
            registration.setManagementNodes(["a", "b"])
            registration.setRequiredNetwork("1.1.1.1")
            configFile = os.path.join(configD, "requiredNetwork")
            self.failUnlessEqual(file(configFile).read(),
                "requiredNetwork 1.1.1.1\n")
            registration.setRequiredNetwork(None)
            self.failIf(os.path.exists(configFile))
        finally:
            del sys.path[-1]
            del sys.modules['rpath_tools.client']
            del sys.modules['helper_rpath_tools']
        configFile = os.path.join(configD, "directMethod")
        self.failUnlessEqual(file(configFile).read(), """\
directMethod []
directMethod a
directMethod b
""")
