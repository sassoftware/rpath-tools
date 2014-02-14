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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from conary import callbacks as conaryCallbacks
from conary.lib import util

from rpath_tools.client import hardware

from conary_test import rephelp

from testrunner import testcase
from testutils import mock
from rpath_tools.lib import clientfactory, installation_service, jobs, update

class RpathToolsMixIn(object):
    def setUp(self):
        IP = hardware.HardwareData.IP
        mockHardwareData = mock.MockObject()
        mockHardwareData.getIpAddresses._mock.setDefaultReturn([
            IP(ipv4='1.1.1.1', netmask='255.255.255.0', device='eth0',
                dns_name='host1.com',),
            IP(ipv4='2.2.2.2', netmask='255.255.0.0', device='eth1',
                dns_name='host2.com',),
            IP(ipv4='3.3.3.3', netmask='255.255.0.0', device='eth2',
                dns_name='host3.com',),
        ])
        mockHardwareData.getHostname._mock.setDefaultReturn('localhost.localdomain')
        mockHardwareData.getLocalIp._mock.setDefaultReturn('2.2.2.2')
        mockHardwareData.getDeviceName._mock.setDefaultReturn('oaia aia e a ei')

        self.mock(hardware, 'HardwareData', mock.MockObject())
        hardware.HardwareData._mock.setDefaultReturn(mockHardwareData)

    def tearDown(self):
        pass

    def setUpRpathToolsConfig(self):
        topDir = self.workDir + '/temp'
        configD = os.path.join(topDir, 'config.d')
        util.mkdirChain(configD)
        configFilePath = os.path.join(topDir, "config")
        file(configFilePath, "w").write("""\
topDir %(topDir)s
logFile %(topDir)s/log
conaryProxyFilePath %(topDir)s/rpath-tools-conaryProxy
remoteCertificateAuthorityStore %(topDir)s/certs
scannerSurveyStore %(workDir)s/storage/surveys
scannerSurveyLockFile %(topDir)s/survey.lock
sfcbConfigurationFile %(topDir)s/sfcb.cfg
includeConfigFile %(configD)s/*
""" % dict(topDir=topDir, configD=configD, workDir=self.workDir))
        file(os.path.join(topDir, "sfcb.cfg"), "w").write("""
sslCertificateFilePath: %(topDir)s/sfcb.ssl
""" % dict(topDir=topDir))
        file(os.path.join(topDir, "sfcb.ssl"), "w").write("blah")
        # This is silly, template locations should be part of the config
        from rpath_tools.client.sysdisco import configurators
        checkedOutTemplates = os.path.join(os.path.dirname(configurators.__file__),
                '..', '..', '..', '..', 'xml_resources', 'templates')
        if os.path.isdir(checkedOutTemplates):
            self.mock(configurators, 'templatePath', checkedOutTemplates)
            self.mock(configurators, 'writeErrorTemplate',
                    os.path.join(checkedOutTemplates,
                        os.path.basename(configurators.writeErrorTemplate)))
            self.mock(configurators, 'readErrorTemplate',
                    os.path.join(checkedOutTemplates,
                        os.path.basename(configurators.readErrorTemplate)))
            self.mock(configurators, 'validateErrorTemplate',
                    os.path.join(checkedOutTemplates,
                        os.path.basename(configurators.validateErrorTemplate)))
            self.mock(configurators, 'discoverErrorTemplate',
                    os.path.join(checkedOutTemplates,
                        os.path.basename(configurators.discoverErrorTemplate)))
            self.mock(configurators, 'xslFilePath',
                    os.path.join(checkedOutTemplates, '..',
                        os.path.basename(configurators.xslFilePath)))
            extensionDir = os.path.join(self.workDir, 'rpath-tools', 'extensions')
            self.mock(configurators, 'readExtensionPath',
                    os.path.join(extensionDir,
                        os.path.basename(configurators.readExtensionPath)))
            self.mock(configurators, 'writeExtensionPath',
                    os.path.join(extensionDir,
                        os.path.basename(configurators.writeExtensionPath)))
            self.mock(configurators, 'discoverExtensionPath',
                    os.path.join(extensionDir,
                        os.path.basename(configurators.discoverExtensionPath)))
            self.mock(configurators, 'validateExtensionPath',
                    os.path.join(extensionDir,
                        os.path.basename(configurators.validateExtensionPath)))
            valuesXmlPath = os.path.join(self.workDir, 'rpath-tools', 'values.xml')
            self.mock(configurators, 'valuesXmlPath', valuesXmlPath)

        return configFilePath

class TestCase(RpathToolsMixIn, testcase.TestCaseWithWorkDir):
    def setUp(self):
        testcase.TestCaseWithWorkDir.setUp(self)
        RpathToolsMixIn.setUp(self)

class TestCaseRepo(RpathToolsMixIn, rephelp.RepositoryHelper):
    def setUp(self):
        rephelp.RepositoryHelper.setUp(self)
        RpathToolsMixIn.setUp(self)
        self.openRepository()
        self._conaryClient = self.getConaryClient()
        util.mkdirChain(os.path.dirname(self._conaryClient.cfg.root + self._conaryClient.cfg.modelPath))
        self._conaryClient.setUpdateCallback(conaryCallbacks.UpdateCallback())

        # Create a Conary client that can talk to the testsuite repo
        class ConaryClientFactory(clientfactory.ConaryClientFactory):
            def getClient(slf, *args, **kwargs):
                return self._conaryClient
            def getCfg(slf, *args, **kwargs):
                return self._conaryClient.cfg

        self.mock(update.UpdateService, 'conaryClientFactory', ConaryClientFactory)
        self.storagePath = os.path.join(self.workDir, "storage")
        self.mock(installation_service.UpdateSet, "storagePath", self.storagePath)
        self.mock(jobs.BaseUpdateTask, "storagePath", self.storagePath)

    def setUpRpathTools(self, configFilePathArg):
        class SurveyTask(jobs.SurveyTask):
            class surveyServiceFactory(jobs.surveys.SurveyService):
                def __init__(self, configFilePath=None):
                    if configFilePath is None:
                        configFilePath = configFilePathArg
                    jobs.surveys.SurveyService.__init__(self, configFilePath=configFilePath)
        self.mock(jobs, 'SurveyTask', SurveyTask)

    def tearDown(self):
        RpathToolsMixIn.tearDown(self)
        rephelp.RepositoryHelper.tearDown(self)

    def setupRepo(self):
        for v in ["1", "2"]:
            trv = self.addComponent("foo:runtime", v)
            self.addCollection("foo", trv.version.freeze(), [":runtime"])
            self.addCollection("group-foo", v, [ "foo" ])
            trv = self.addComponent("bar:runtime", v)
            self.addCollection("bar", trv.version.freeze(), [":runtime"])
            self.addCollection("group-bar-appliance", v, [ "bar" ])
