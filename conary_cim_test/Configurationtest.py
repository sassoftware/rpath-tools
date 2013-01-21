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


import pywbem
import config_manager

import testbase
import config_managertest

import os

class TestConfiguration(testbase.TestCaseProvider, config_managertest.ConfigTestMixin):

    def setUp(self):
        testbase.TestCaseProvider.setUp(self)
        config_managertest.ConfigTestMixin.setUp(self)

    def testConfiguration(self):
        prov, objP = self.getProviderConfiguration()

        self.setBinary(failed=False)

        self.failUnlessEqual(
            [ x.keybindings for x in prov.MI_enumInstanceNames(self.env, objP) ],
            [ dict(
                CreationClassName = 'RPATH_Configuration',
                SettingID = config_manager.ConfigManager.ConfigFilePath,
                SystemName = 'localhost.localdomain',
                SystemCreationClassName = 'Linux_ComputerSystem') ])

        self.failUnlessEqual(
            [ x.path['SettingID'] for x in prov.MI_enumInstances(self.env, objP, []) ],
            [ config_manager.ConfigManager.ConfigFilePath ])

        self.failUnlessEqual(
            [
                dict((key, val.value) for (key, val) in x.properties.items())
                    for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Value = None)])

        # Set a value
        file(config_manager.ConfigManager.ConfigFilePath, "w").write("<value/>")

        self.failUnlessEqual(
            [
                dict((key, val.value) for (key, val) in x.properties.items())
                    for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Value = "<value/>")])

    def testSetInstance(self):
        prov, objP = self.getProviderConfiguration()

        instance = prov.MI_enumInstances(self.env, objP, []).next()
        instance.properties['Value'] = pywbem.CIMProperty('Value',
            '<newvalue/>', type='string')
        ninstance = prov.MI_modifyInstance(self.env, instance,
            propertyList=None)

        self.failUnlessEqual(
            [
                dict((key, val.value) for (key, val) in x.properties.items())
                    for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Value = "<newvalue/>")])

        # Set a value
        file(config_manager.ConfigManager.ConfigFilePath, "w").write("<value/>")

        self.failUnlessEqual(
            [
                dict((key, val.value) for (key, val) in x.properties.items())
                    for x in prov.MI_enumInstances(self.env, objP, []) ],
            [dict(Value = "<value/>")])


    def testApply(self):
        prov, objP = self.getProviderConfiguration()

        objP.keybindings['SettingID'] = config_manager.ConfigManager.ConfigFilePath
        self.setBinary(failed=False)
        ret = prov.MI_invokeMethod(self.env, objP, 'ApplyToMSE', dict())
        self.assertEquals(ret[0], ('uint16', 0))
        self.assertEquals(ret[1].keys(), ['operationlogs'])

        self.setBinary(failed=True)
        ret = prov.MI_invokeMethod(self.env, objP, 'ApplyToMSE', dict())
        self.assertEquals(ret[0], ('uint16', 64L))
        self.assertEquals(ret[1].keys(), ['operationlogs'])
