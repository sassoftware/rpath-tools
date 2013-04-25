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

import RPATH_SoftwareInstallationService as rSIS
import RPATH_UpdateConcreteJob as rUpdateConcreteJob
import RPATH_SurveyConcreteJob as rSurveyConcreteJob
import RPATH_ElementSoftwareIdentity as rESI
import RPATH_SoftwareIdentity as rSI
import RPATH_RecordLog as rRL
import RPATH_LogEntry as rLE
import RPATH_UseOfLog as rUoL
import RPATH_ComputerSystem as rCS
import RPATH_Configuration as rCfg
import RPATH_SystemSurvey as rSysSurvey
import RPATH_SystemSurveyService as rSysSurveyService

from rpath_toolstest import testbase

class TestCase(testbase.TestCase):
    pass

class Logger(object):

    def log_debug(self, *args, **kwargs):
        return self._log("debug", *args, **kwargs)

    def log_info(self, *args, **kwargs):
        return self._log("info", *args, **kwargs)

    def log_error(self, *args, **kwargs):
        return self._log("error", *args, **kwargs)

    def _log(self, level, *args, **kwargs):
        pass

class CimomHandle(object):
    ns = "root/cimv2"
    instances = {
        (ns, "Linux_ComputerSystem") : [
            ("Linux_ComputerSystem",
                dict(Name = 'localhost.localdomain',
                     CreationClassName = 'Linux_ComputerSystem'),
                dict(ElementName = 'localhost.localdomain')),
        ]
    }
    instances[(ns, 'CIM_ComputerSystem')] = instances[(ns, 'Linux_ComputerSystem')]

    def EnumerateInstanceNames(self, ns, classname):
        return self._enum(ns, classname, keys_only=True)

    def EnumerateInstances(self, ns, classname):
        return self._enum(ns, classname, keys_only=False)

    def _enum(self, ns, classname, keys_only=True):
        if (ns, classname) not in self.instances:
            raise Exception("Mock me! %s" % classname)
        for className, keybindings, props in self.instances[(ns, classname)]:
            op = pywbem.CIMInstanceName(className, keybindings = keybindings,
                namespace = ns)
            if keys_only:
                yield op
            else:
                inst = pywbem.CIMInstance(className, properties = props,
                    path = op)
                inst.update(keybindings)
                yield inst

class Environment(object):
    loggerClass = Logger
    cimomHandleClass = CimomHandle

    def get_logger(self):
        return self.loggerClass()

    def get_cimom_handle(self):
        return self.cimomHandleClass()


class ProviderMixIn(object):
    def setUp(self):
        self.env = Environment()

    def tearDown(self):
        self.env = None

    def getProvider(self, module):
        """Given a module, return the provider and an object path"""
        cimClassName, prov = sorted(module.get_providers(self.env).items())[0]
        objPath = pywbem.CIMInstanceName(cimClassName)
        return prov, objPath

    def getProviderSoftwareInstallationService(self):
        return self.getProvider(rSIS)

    def getProviderElementSoftwareIdentity(self):
        return self.getProvider(rESI)

    def getProviderUpdateConcreteJob(self):
        return self.getProvider(rUpdateConcreteJob)

    def getProviderSurveyConcreteJob(self):
        return self.getProvider(rSurveyConcreteJob)

    def getProviderSoftwareIdentity(self):
        return self.getProvider(rSI)

    def getProviderRecordLog(self):
        return self.getProvider(rRL)

    def getProviderLogEntry(self):
        return self.getProvider(rLE)

    def getProviderUseOfLog(self):
        return self.getProvider(rUoL)

    def getProviderComputerSystem(self):
        return self.getProvider(rCS)

    def getProviderConfiguration(self):
        return self.getProvider(rCfg)

    def getProviderSystemSurvey(self):
        return self.getProvider(rSysSurvey)

    def getProviderSystemSurveyService(self):
        return self.getProvider(rSysSurveyService)

class TestCaseProvider(TestCase, ProviderMixIn):
    def setUp(self):
        TestCase.setUp(self)
        ProviderMixIn.setUp(self)
