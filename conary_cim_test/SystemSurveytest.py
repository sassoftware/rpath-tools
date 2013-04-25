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
from conary import trovetup
from conary.lib import util
from lxml import etree

import testbaserepo

import pywbem
import time
from rpath_tools.lib import jobs, surveys

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

    def _invokeScan(self, desiredTopLevelItems=None, systemModel=None):
        prov, objP  = self.getProviderSystemSurveyService()

        args = dict()
        if systemModel is not None:
            args.update(SystemModel=systemModel)
        elif desiredTopLevelItems is not None:
            args.update(DesiredPackages=desiredTopLevelItems)

        # Invoke method
        ret, params = prov.MI_invokeMethod(self.env, objP, "Scan", args)
        self.failUnlessEqual(ret[1], 4096)
        jobOP = params['job'][1]
        ret, jobO, job = self.waitJob(jobOP)
        self.assertEquals(ret, 4)
        # For some reason the CIM job is marked as finished, but the one
        # on disk is not
        for i in range(20):
            if job._task.job.state in set(['Completed', 'Exception']):
                break
            time.sleep(0.2)
        self.assertEquals(job._task.job.state, 'Completed')
        surveyId = job._task.job.content
        svc = surveys.SurveyService()
        survey = svc.load(surveyId)
        return survey

    def _troveTup(self, trvTup):
        if isinstance(trvTup, trovetup.TroveTuple):
            return trvTup
        return trovetup.TroveTuple((trvTup))

    def testSystemSurveyService_scan(self):
        self.setupRepo()
        self.updatePkg(["foo=1", "group-bar-appliance=1"])
        configFilePath = self.setUpRpathToolsConfig()
        self.setUpRpathTools(configFilePath)
        survey = self._invokeScan()

        doc = etree.fromstring(survey.content)
        rpmPackagesNode = doc.find('rpm_packages')
        self.assertEquals([ x for x in rpmPackagesNode ], [])
        conaryPackagesNode = doc.find('conary_packages')
        self.assertEquals(set(x.attrib['id'] for x in conaryPackagesNode),
            set(str(x) for x in range(5)))
        self.assertEquals(
                set(x.find('conary_package_info').find('name').text
                    for x in conaryPackagesNode),
                set(['bar', 'bar:runtime',
                     'foo', 'foo:runtime',
                     'group-bar-appliance',
                     ]))

    def testSystemSurveyService_scan_withDesiredTopLevelItems(self):
        self.setupRepo()
        repos = self.openRepository()
        trvTup = repos.findTrove(self.defLabel, ('group-bar-appliance', '2', None))[0]
        trvTup = self._troveTup(trvTup)
        desiredTopLevelItems = [ trvTup.asString() ]

        self.updatePkg(["foo=1", "group-bar-appliance=1"])
        configFilePath = self.setUpRpathToolsConfig()
        self.setUpRpathTools(configFilePath)
        survey = self._invokeScan(desiredTopLevelItems=desiredTopLevelItems)

        doc = etree.fromstring(survey.content)
        rpmPackagesNode = doc.find('rpm_packages')
        self.assertEquals([ x for x in rpmPackagesNode ], [])
        conaryPackagesNode = doc.find('conary_packages')
        self.assertEquals(set(x.attrib['id'] for x in conaryPackagesNode),
            set(str(x) for x in range(5)))
        self.assertEquals(
                set(x.find('conary_package_info').find('name').text
                    for x in conaryPackagesNode),
                set(['bar', 'bar:runtime',
                     'foo', 'foo:runtime',
                     'group-bar-appliance',
                     ]))

    def testSystemSurveyServiceWithSystemModel_scan(self):
        self.setupRepo()
        repos = self.openRepository()
        fooSpec = ('foo', '1', None)
        groupSpec = ('group-bar-appliance', '1', None)
        ret = repos.findTroves(self.defLabel, [ fooSpec, groupSpec ])
        sysModelItems = []
        for spec in [ groupSpec, fooSpec ]:
            trvTup = ret[spec][0]
            trvTup = self._troveTup(trvTup)
            sysModelItems.append(trvTup.asString())
        systemModel = '\n'.join('install %s' % (x, ) for x in sysModelItems)
        systemModelPath = util.joinPaths(self.cfg.root, self.cfg.modelPath)
        util.mkdirChain(os.path.dirname(systemModelPath))
        file(systemModelPath, 'w').write(systemModel)

        self.updatePkg(["foo=1", "group-bar-appliance=1"])
        configFilePath = self.setUpRpathToolsConfig()
        self.setUpRpathTools(configFilePath)
        survey = self._invokeScan()

        doc = etree.fromstring(survey.content)
        rpmPackagesNode = doc.find('rpm_packages')
        self.assertEquals([ x for x in rpmPackagesNode ], [])
        conaryPackagesNode = doc.find('conary_packages')
        self.assertEquals(set(x.attrib['id'] for x in conaryPackagesNode),
            set(str(x) for x in range(5)))
        self.assertEquals(
                set(x.find('conary_package_info').find('name').text
                    for x in conaryPackagesNode),
                set(['bar', 'bar:runtime',
                     'foo', 'foo:runtime',
                     'group-bar-appliance',
                     ]))

    def testSystemSurveyServiceWithSystemModel_scan_withSystemModel(self):
        self.setupRepo()
        repos = self.openRepository()
        fooSpec = ('foo', '1', None)
        groupSpec = ('group-bar-appliance', '1', None)
        groupSpec2 = ('group-bar-appliance', '2', None)
        ret = repos.findTroves(self.defLabel, [ fooSpec, groupSpec, groupSpec2 ])
        sysModelItems = []
        for spec in [ groupSpec, fooSpec ]:
            trvTup = ret[spec][0]
            trvTup = self._troveTup(trvTup)
            sysModelItems.append(trvTup.asString())
        systemModel = '\n'.join('install %s' % (x, ) for x in sysModelItems)
        systemModelPath = util.joinPaths(self.cfg.root, self.cfg.modelPath)
        util.mkdirChain(os.path.dirname(systemModelPath))
        file(systemModelPath, 'w').write(systemModel)

        trvTup = ret[groupSpec2][0]
        trvTup = self._troveTup(trvTup)
        newSystemModel = "install %s" % trvTup.asString()

        self.updatePkg(["foo=1", "group-bar-appliance=1"])
        configFilePath = self.setUpRpathToolsConfig()
        self.setUpRpathTools(configFilePath)
        survey = self._invokeScan(systemModel=newSystemModel)

        doc = etree.fromstring(survey.content)
        rpmPackagesNode = doc.find('rpm_packages')
        self.assertEquals([ x for x in rpmPackagesNode ], [])
        conaryPackagesNode = doc.find('conary_packages')
        self.assertEquals(set(x.attrib['id'] for x in conaryPackagesNode),
            set(str(x) for x in range(5)))
        self.assertEquals(
                set(x.find('conary_package_info').find('name').text
                    for x in conaryPackagesNode),
                set(['bar', 'bar:runtime',
                     'foo', 'foo:runtime',
                     'group-bar-appliance',
                     ]))
        preview = doc.find('preview')
        self.assertEquals(
                [ trovetup.TroveTuple(x.text).asString()
                    for x in preview.iterchildren('observed') ],
                ['foo=/localhost@rpl:linux/1-1-1[]',
                    'group-bar-appliance=/localhost@rpl:linux/1-1-1[]'])
        self.assertEquals(
                [ trovetup.TroveTuple(x.text).asString()
                    for x in preview.iterchildren('desired') ],
                # This is correct even though the test fails - we need
                # to fix the code
                ['group-bar-appliance=/localhost@rpl:linux/2-1-1[]'])
