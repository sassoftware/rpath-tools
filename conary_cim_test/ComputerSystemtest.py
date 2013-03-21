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
import helper_rpath_tools
import testbase
from rpath_tools.client import command, register

class TestComputerSystem(testbase.TestCaseProvider):
    def setUp(self):
        testbase.TestCaseProvider.setUp(self)
        configFilePath = self.setUpRpathToolsConfig()

        origRegistration = helper_rpath_tools.Registration
        self.registration = origRegistration(configFilePath)
        class MockRegistration(origRegistration):
            def __new__(slf, event_uuid=None):
                self.registration.event_uuid = event_uuid
                return self.registration
        self.mock(helper_rpath_tools, 'Registration', MockRegistration)
        self.mock(command.RegistrationCommand, 'scanSystem', lambda *args, **kw: None)
        self.mock(register.Registration, 'registerSystem', lambda *args, **kwargs: True)

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
                LocalUUID = 'my-uuid',
                GeneratedUUID = self.registration.generatedUuid,
                ElementName = 'localhost.localdomain', ), ])

        # Now pretend the provider can load rpath_tools
        try:
            self.failUnlessEqual(
                [
                    dict((key, val.value)
                        for (key, val) in x.properties.items())
                            for x in prov.MI_enumInstances(self.env, objP, []) ],
                [dict(Name = 'localhost.localdomain',
                    CreationClassName = 'RPATH_ComputerSystem',
                    ElementName = 'localhost.localdomain',
                    LocalUUID = 'my-uuid',
                    GeneratedUUID = self.registration.generatedUuid,),
                ])
            ret = prov.MI_invokeMethod(self.env, objP, 'RemoteRegistration',
                    dict(ManagementNodeAddresses=['1.2.3.4:9443', '2.2.2.2:9443'],
                    RequiredNetwork='1.1.1.1',
                    EventUUID='uuid007'))
            self.failUnlessEqual(ret, (('uint16', 0L), {}))

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "directMethod")
            self.failUnlessEqual(file(configFilePath).read(),
                    'directMethod []\ndirectMethod 1.2.3.4:9443\ndirectMethod 2.2.2.2:9443\n')

            configFilePath = self.registration.cfg.conaryProxyFilePath
            self.failUnlessEqual(file(configFilePath).read(),
                'proxyMap * conarys://1.2.3.4 conarys://2.2.2.2\n')

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "requiredNetwork")
            self.failUnlessEqual(file(configFilePath).read(), 'requiredNetwork 1.1.1.1\n')
            self.failUnlessEqual(self.registration.event_uuid, 'uuid007')
        finally:
            pass

    def testComputerSystemRemoteRegistration(self):
        prov, objP = self.getProviderComputerSystem()

        try:
            ret = prov.MI_invokeMethod(self.env, objP, 'RemoteRegistration',
                    dict(ManagementNodeAddresses=['1.2.3.4:9443', '2.2.2.2:9443'],
                    RequiredNetwork='1.1.1.1',
                    EventUUID='uuid007'))
            self.failUnlessEqual(ret, (('uint16', 0L), {}))

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "directMethod")
            self.failUnlessEqual(file(configFilePath).read(),
                    'directMethod []\ndirectMethod 1.2.3.4:9443\ndirectMethod 2.2.2.2:9443\n')

            configFilePath = self.registration.cfg.conaryProxyFilePath
            self.failUnlessEqual(file(configFilePath).read(),
                'proxyMap * conarys://1.2.3.4 conarys://2.2.2.2\n')

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "requiredNetwork")
            self.failUnlessEqual(file(configFilePath).read(), 'requiredNetwork 1.1.1.1\n')
            self.failUnlessEqual(self.registration.event_uuid, 'uuid007')

            # Now test an exception
            def fakeRegisterSystem(*args, **kwargs):
                raise Exception("Some value")
            self.mock(register.Registration, 'registerSystem', fakeRegisterSystem)
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
            pass

    def testComputerSystem_UpdateManagementConfiguration(self):
        prov, objP = self.getProviderComputerSystem()
        try:
            ret = prov.MI_invokeMethod(self.env, objP,
                'UpdateManagementConfiguration',
                dict(ManagementNodeAddresses=['1.2.3.4:9443', '2.2.2.2:9443'],
                    RequiredNetwork='1.1.1.1'))
            self.failUnlessEqual(ret, (('uint16', 0L), {}))

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "directMethod")
            self.failUnlessEqual(file(configFilePath).read(),
                    'directMethod []\ndirectMethod 1.2.3.4:9443\ndirectMethod 2.2.2.2:9443\n')

            configFilePath = self.registration.cfg.conaryProxyFilePath
            self.failUnlessEqual(file(configFilePath).read(),
                'proxyMap * conarys://1.2.3.4 conarys://2.2.2.2\n')

            configFilePath = os.path.join(self.registration.cfg.topDir,
                    self.registration.CONFIG_D_DIRECTORY, "requiredNetwork")
            self.failUnlessEqual(file(configFilePath).read(),
                'requiredNetwork 1.1.1.1\n')

        finally:
            pass
