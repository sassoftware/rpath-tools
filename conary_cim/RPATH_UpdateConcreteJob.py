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

    def cim_method_applyupdate(self, env, object_name):
        """Implements RPATH_UpdateConcreteJob.ApplyUpdate()

        Apply an update job.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ApplyUpdate() 
            should be invoked.

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.ApplyUpdate)
        and a list of CIMParameter objects representing the output parameters

        Output parameters: none

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, 
            unrecognized or otherwise incorrect parameters)
        CIM_ERR_NOT_FOUND (the target CIM Class or instance does not 
            exist in the specified namespace)
        CIM_ERR_METHOD_NOT_AVAILABLE (the CIM Server is unable to honor 
            the invocation request)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.cim_method_applyupdate()' \
                % self.__class__.__name__)

        key = object_name.keybindings.get('InstanceID')
        if not key:
            rval = self.Values.ApplyUpdate.Failed
            return (rval, [])

        key = self.fromInstanceID(key)
        self.concreteJob = concrete_job.UpdateJob.applySyncOperation(key)

        cuJob = self.concreteJob.concreteJob
        if cuJob.state != "Exception":
            rval = self.Values.ApplyUpdate.OK
            return (rval, [])

        rval = self.Values.ApplyUpdate.Failed
        return (rval, [])

## get_providers() for associating CIM Class Name to python provider class name

def get_providers(env):
    rpath_updateconcretejob_prov = RPATH_UpdateConcreteJob(env)
    return {
        'RPATH_UpdateConcreteJob': rpath_updateconcretejob_prov,
    }
