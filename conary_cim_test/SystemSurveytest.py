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

import testbaserepo

import pywbem
from rpath_tools.lib import installation_service, jobs
import surveys

class Test(testbaserepo.TestCase):
    def setUp(self):
        testbaserepo.TestCase.setUp(self)
        self.surveyStoragePath = os.path.join(self.workDir, "storage")
        self.mock(surveys.SurveyService, 'storagePath', self.surveyStoragePath)
        self.mock(jobs.SurveyTask, 'storagePath', self.surveyStoragePath)
        self.surveyPath = os.path.join(self.surveyStoragePath,
            surveys.Survey.prefix)
        os.makedirs(self.surveyPath)

    def testSystemSurvey(self):
        for surveyId in [ 'aaa', 'bbb', 'ccc' ]:
            file(os.path.join(self.surveyPath, "survey-%s.xml" % surveyId), "w").write(surveyId)
        prov, objP  = self.getProviderSystemSurvey()
        # Heh. Because the provider reuses the model object, we need to
        # copy the keybindings
        self.failUnlessEqual(
            [ x.keybindings.copy() for x in prov.MI_enumInstanceNames(self.env, objP) ],
            [
                {'InstanceID' : 'com.rpath:surveys/aaa'},
                {'InstanceID' : 'com.rpath:surveys/bbb'},
                {'InstanceID' : 'com.rpath:surveys/ccc'},
        ])

        self.failUnlessEqual(
            [ dict(inst.iteritems())
                for inst in prov.MI_enumInstances(self.env, objP, []) ],
            [
                {'InstanceID' : 'com.rpath:surveys/aaa', 'Value' : 'aaa'},
                {'InstanceID' : 'com.rpath:surveys/bbb', 'Value' : 'bbb'},
                {'InstanceID' : 'com.rpath:surveys/ccc', 'Value' : 'ccc'},
        ])

        inst = prov.MI_getInstance(self.env, objP, None)
        self.failUnlessEqual(
            dict(inst.iteritems()),
            {'InstanceID' : 'com.rpath:surveys/ccc', 'Value' : 'ccc'},
        )

        error = self.failUnlessRaises(pywbem.CIMError,
            prov.MI_createInstance, self.env, objP)
        self.failUnlessEqual(error.args, (7, ))
        error = self.failUnlessRaises(pywbem.CIMError,
            prov.MI_modifyInstance, self.env, inst, [])
        self.failUnlessEqual(error.args, (7, ))
        error = self.failUnlessRaises(pywbem.CIMError,
            prov.MI_deleteInstance, self.env, objP)
        self.failUnlessEqual(error.args, (7, ))

    def testSystemSurveyService(self):
        prov, objP  = self.getProviderSystemSurveyService()
        self.failUnlessEqual(
            [ x.keybindings.copy() for x in prov.MI_enumInstanceNames(self.env, objP) ],
            [
                {
                    'CreationClassName': 'RPATH_SystemSurveyService',
                    'SystemName': 'localhost.localdomain',
                    'Name': 'rPath System Survey Service',
                    'SystemCreationClassName': 'Linux_ComputerSystem',
                }
        ])

        inst = prov.MI_getInstance(self.env, objP, None)
        self.failUnlessEqual(
            dict(inst.iteritems()),
            {
                    'CreationClassName': 'RPATH_SystemSurveyService',
                    'SystemName': 'localhost.localdomain',
                    'Name': 'rPath System Survey Service',
                    'SystemCreationClassName': 'Linux_ComputerSystem',
            }
        )

        unsupportedMethods = [
            ("RequestStateChange", {}),
            ("StartService", {}),
            ("StopService", {}),
            ("ChangeAffectedElementsAssignedSequence",
                dict(ManagedElements = [], AssignedSequence = [])),
        ]
        for method, params in unsupportedMethods:
            error = self.failUnlessRaises(pywbem.CIMError,
                prov.MI_invokeMethod, self.env, objP, method, params)
            self.failUnlessEqual(error.args, (16, ))

    def testSystemSurveyService_scan(self):
        prov, objP  = self.getProviderSystemSurveyService()

        # Invoke method
        ret, params = prov.MI_invokeMethod(self.env, objP, "Scan", {})
        self.failUnlessEqual(ret[1], 4096)
