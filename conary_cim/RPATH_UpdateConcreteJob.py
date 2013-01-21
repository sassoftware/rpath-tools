#!/usr/bin/python2.4
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

import pywbem
import concrete_job
import baseConcreteJobProvider
import stub_RPATH_UpdateConcreteJob

stubClass = stub_RPATH_UpdateConcreteJob.RPATH_UpdateConcreteJob

class RPATH_UpdateConcreteJob(baseConcreteJobProvider.ConcreteJobMixIn, stubClass):
    """Instrument the CIM class RPATH_UpdateConcreteJob 

    A concrete version of Job. This class represents a generic and
    instantiable unit of work, such as a batch or a print job.
    
    """

    JobName = "Update Job"

    def __init__ (self, env):
        stubClass.__init__(self, env)
        self.concreteJob = concrete_job.UpdateJob()

    def produceResults(self, env, model, job):
        if job.content is None:
            return
        model['JobResults'] =  pywbem.CIMProperty('JobResults',
            [ job.content ])

## get_providers() for associating CIM Class Name to python provider class name

def get_providers(env):
    rpath_updateconcretejob_prov = RPATH_UpdateConcreteJob(env)
    return {
        'RPATH_UpdateConcreteJob': rpath_updateconcretejob_prov,
    }
