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


import testbase

import os

class TestComputerSystem(testbase.TestCaseProvider):
    def testComputerSystem(self):
        prov, objP = self.getProviderComputerSystem()
        self.failUnlessEqual(
            [ x.keybindings for x in prov.MI_enumInstanceNames(self.env, objP) ],
            [dict(Name = 'localhost.localdomain',
                CreationClassName = 'RPATH_ComputerSystem'), ])
        self.failUnlessEqual(
            [ x.path.keybindings for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Name = 'localhost.localdomain',
                CreationClassName = 'RPATH_ComputerSystem'), ])
        self.failUnlessEqual(
            [
                dict((key, val.value) for (key, val) in x.properties.items())
                    for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Name = 'localhost.localdomain',
                CreationClassName = 'RPATH_ComputerSystem',
                ElementName = 'localhost.localdomain', ), ])

        # Now pretend the provider can load rpath_tools
        class fakeHelperRpathTools(object):
            class Registration(object):
                localUuid = '01020300'
                generatedUuid = '01020301'
                _methodsCalled = []

                def __init__(self, *args, **kwargs):
                    self._methodsCalled.append(('__init__', args, kwargs))

                @classmethod
                def _invoke(cls, methodName, args, kwargs):
                    cls._methodsCalled.append((methodName, args, kwargs))

                def setManagementNodes(self, *args, **kwargs):
                    self._invoke('setManagementNodes', args, kwargs)

                def setRequiredNetwork(self, *args, **kwargs):
                    self._invoke('setRequiredNetwork', args, kwargs)

                def setConaryProxy(self, *args, **kwargs):
                    self._invoke('setConaryProxy', args, kwargs)

                def run(slf, *args, **kwargs):
                    slf._invoke('run', args, kwargs)

        # Now pretend the provider can load rpath_tools
        import sys
        try:
            sys.modules['helper_rpath_tools'] = fakeHelperRpathTools

            self.failUnlessEqual(
                [
                    dict((key, val.value)
                        for (key, val) in x.properties.items())
                            for x in prov.MI_enumInstances(self.env, objP, []) ],
                [dict(Name = 'localhost.localdomain',
                    CreationClassName = 'RPATH_ComputerSystem',
                    ElementName = 'localhost.localdomain',
                    LocalUUID = '01020300',
                    GeneratedUUID = '01020301',),
                ])
            ret = prov.MI_invokeMethod(self.env, objP, 'RemoteRegistration',
                dict(ManagementNodeAddresses=['1', '2'],
                    RequiredNetwork='1',
                    EventUUID='uuid007'))
            self.failUnlessEqual(fakeHelperRpathTools.Registration._methodsCalled,
                [
                    ('__init__', (), {}),
                    ('__init__', (), {}),
                    ('setManagementNodes', (['1', '2'],), {}),
                    ('setConaryProxy', (['1', '2'],), {}),
                    ('setRequiredNetwork', ('1',), {}),
                    ('__init__', (), {'event_uuid' : 'uuid007'}),
                    ('run', (), {})
                ])
            self.failUnlessEqual(ret, (('uint16', 0L), {}))
        finally:
            del sys.modules['helper_rpath_tools']

    def testComputerSystemRemoteRegistration(self):
        prov, objP = self.getProviderComputerSystem()

        fakeRpathTools = self._getFakeRpathTools(self.workDir)
        config_d_directory =  os.path.join(self.workDir, 'config.d')
        os.mkdir(config_d_directory)
        import sys
        try:
            sys.modules['rpath_tools'] = fakeRpathTools
            sys.modules['rpath_tools.client'] = fakeRpathTools.client
            import helper_rpath_tools
            origConfigDir = helper_rpath_tools.Registration.CONFIG_D_DIRECTORY
            helper_rpath_tools.Registration.CONFIG_D_DIRECTORY = config_d_directory

            ret = prov.MI_invokeMethod(self.env, objP, 'RemoteRegistration',
                dict(ManagementNodeAddresses=['1', '2'],
                    RequiredNetwork='1',
                    EventUUID='uuid007'))
            self.failUnlessEqual(ret, (('uint16', 0L), {}))
            methodsCalled = fakeRpathTools.client.main.RpathToolsMain._methodsCalled
            self.failUnless(isinstance(methodsCalled[0][1][0],
                fakeRpathTools.client.command.RegistrationCommand))
            self.failUnless(isinstance(methodsCalled[0][1][1],
                fakeRpathTools.client.config.RpathToolsConfiguration))
            self.failUnlessEqual([ (x[0], x[1][2:]) for x in methodsCalled ],
                [('run', ({'force' : True, 'event-uuid' : 'uuid007'}, ()))])

            # Now test an exception
            class RpathToolsMain(object):
                def runCommand(slf, *args, **kwargs):
                    raise Exception("Some value")
            fakeRpathTools.client.main.RpathToolsMain = RpathToolsMain

            ret = self.discardOutput(prov.MI_invokeMethod,
                self.env, objP, 'RemoteRegistration',
                dict(ManagementNodeAddresses=['1', '2'],
                    RequiredNetwork='1'))
            self.failUnlessEqual(ret[0], ('uint16', 1L))
            self.failUnlessEqual(ret[1]['errorSummary'],
                ('string', 'Error registering: Some value'))
            errorDetailsType, errorDetails = ret[1]['errorDetails']
            self.failUnlessEqual(errorDetailsType, 'string')
            self.failUnless(errorDetails.startswith(
                'Traceback (most recent call last):'),
                errorDetails)
        finally:
            del sys.modules['rpath_tools']
            del sys.modules['rpath_tools.client']
            helper_rpath_tools.Registration.CONFIG_D_DIRECTORY = origConfigDir
            del sys.modules['helper_rpath_tools']

    def testComputerSystem_UpdateManagementConfiguration(self):
        prov, objP = self.getProviderComputerSystem()

        fakeRpathTools = self._getFakeRpathTools(self.workDir)
        config_d_directory =  os.path.join(self.workDir, 'config.d')
        os.mkdir(config_d_directory)
        import sys
        try:
            sys.modules['rpath_tools'] = fakeRpathTools
            sys.modules['rpath_tools.client'] = fakeRpathTools.client
            import helper_rpath_tools
            origConfigDir = helper_rpath_tools.Registration.CONFIG_D_DIRECTORY
            helper_rpath_tools.Registration.CONFIG_D_DIRECTORY = config_d_directory

            ret = prov.MI_invokeMethod(self.env, objP,
                'UpdateManagementConfiguration',
                dict(ManagementNodeAddresses=['1', '2'],
                    RequiredNetwork='1'))
            self.failUnlessEqual(ret, (('uint16', 0L), {}))

            configFilePath = os.path.join(config_d_directory,
                "directMethod")
            self.failUnlessEqual(file(configFilePath).read(),
                'directMethod []\ndirectMethod 1\ndirectMethod 2\n')

            configFilePath = os.path.join(self.workDir, "conary-proxy")
            self.failUnlessEqual(file(configFilePath).read(),
                'conaryProxy https://1\nconaryProxy https://2\n')

            configFilePath = os.path.join(config_d_directory,
                "requiredNetwork")
            self.failUnlessEqual(file(configFilePath).read(),
                'requiredNetwork 1\n')

        finally:
            del sys.modules['rpath_tools']
            del sys.modules['rpath_tools.client']
            helper_rpath_tools.Registration.CONFIG_D_DIRECTORY = origConfigDir
            del sys.modules['helper_rpath_tools']


    @classmethod
    def _getFakeRpathTools(cls, workDir):
        class fakeRpathTools(object):
            class client(object):
                class register(object):
                    class Registration(object):
                        def __init__(slf, *args, **kwargs):
                            pass
                        def getRemote(slf):
                            return 'blah'
                        def setDeviceName(slf, deviceName):
                            return 'eth0'

                class command(object):
                    class RegistrationCommand(object):
                        pass

                class config(object):
                    class RpathToolsConfiguration(object):
                        def __init__(slf, *args, **kwargs):
                            slf.sfcbUrl = "http://blah"
                            slf.conaryProxyFilePath = os.path.join(workDir, 'conary-proxy')

                class hardware(object):
                    class HardwareData(object):
                        def __init__(slf, *args, **kwargs):
                            pass
                        def getLocalIp(slf, remote):
                            return '1.2.3.4'
                        def getDeviceName(slf, localIp):
                            return 'eth0'

                class main(object):
                    class RpathToolsMain(object):
                        _methodsCalled = []
                        def runCommand(slf, *args, **kwargs):
                            slf._methodsCalled.append(('run', args, kwargs))
        return fakeRpathTools
