#!/usr/bin/python
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


"""Python Provider for RPATH_UpdateConcreteJob

Instruments the CIM class RPATH_UpdateConcreteJob

"""

import inspect
import pywbem
from pywbem.cim_provider2 import CIMProvider2

from rpath_tools.lib import jobs
import surveys
import baseConcreteJobProvider
import stub_RPATH_SurveyConcreteJob

stubClass = stub_RPATH_SurveyConcreteJob.RPATH_SurveyConcreteJob

class RPATH_SurveyConcreteJob(baseConcreteJobProvider.ConcreteJobMixIn, stubClass):
    """Instrument the CIM class RPATH_UpdateConcreteJob 

    A concrete version of Job. This class represents a generic and
    instantiable unit of work, such as a batch or a print job.
    
    """

    JobName = "Survey Job"

    def __init__ (self, env):
        stubClass.__init__(self, env)
        self._task = jobs.SurveyTask()
        self.surveyService = surveys.SurveyService()

    def produceResult(self, env, job, surveyUuid):
        import RPATH_SystemSurvey
        survey = self.surveyService.load(surveyUuid)
        return survey.content

def get_providers(env):
    """
    Boilerplate provider registration function.
    Walk the module, find all subclasses of CIMProvider2 and return them
    """
    ret = {}
    for k, v in globals().items():
        if not inspect.isclass(v):
            continue
        if not issubclass(v, CIMProvider2) or v is CIMProvider2 or v is stubClass:
            continue
        prov = v(env)
        ret[k] = prov
    return ret
