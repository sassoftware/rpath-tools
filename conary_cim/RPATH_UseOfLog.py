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


"""Python Provider for RPATH_UseOfLog

Instruments the CIM class RPATH_UseOfLog

"""

import pywbem

import RPATH_RecordLog
import stub_RPATH_UseOfLog
from rpath_tools.lib import jobs
import baseConcreteJobProvider

stubClass = stub_RPATH_UseOfLog.RPATH_UseOfLog

class RPATH_UseOfLog(stubClass):
    """Instrument the CIM class RPATH_ElementSoftwareIdentity 

    ElementSoftwareIdentity allows a Managed Element to report its software
    related asset information (firmware, drivers, configuration software,
    and etc.)
    
    """

    def get_instance(self, env, model, withCleanup=True):
        """Return an instance.

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        model -- A template of the pywbem.CIMInstance to be returned.  The 
            key properties are set on this instance to correspond to the 
            instanceName that was requested.  The properties of the model
            are already filtered according to the PropertyList from the 
            request.  Only properties present in the model need to be
            given values.  If you prefer, you can set all of the 
            values, and the instance will be filtered for you. 

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, unrecognized 
            or otherwise incorrect parameters)
        CIM_ERR_NOT_FOUND (the CIM Class does exist, but the requested CIM 
            Instance does not exist in the specified namespace)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.get_instance()' \
                % self.__class__.__name__)

        return model

    def enum_instances(self, env, model, keys_only):
        """Enumerate instances.

        The WBEM operations EnumerateInstances and EnumerateInstanceNames
        are both mapped to this method. 
        This method is a python generator

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        model -- A template of the pywbem.CIMInstances to be generated.  
            The properties of the model are already filtered according to 
            the PropertyList from the request.  Only properties present in 
            the model need to be given values.  If you prefer, you can 
            always set all of the values, and the instance will be filtered 
            for you. 
        keys_only -- A boolean.  True if only the key properties should be
            set on the generated instances.

        Possible Errors:
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.enum_instances()' \
                % self.__class__.__name__)

        # Prime model.path with knowledge of the keys, so key values on
        # the CIMInstanceName (model.path) will automatically be set when
        # we set property values on the model. 
        model.path.update({'Dependent': None, 'Antecedent': None})

        logClassName = 'RPATH_RecordLog'
        for job in jobs.AnyTask.list():
            # XXX make this more extensible
            if job.keyId.startswith('updates/'):
                jobClassName = 'RPATH_UpdateConcreteJob'
            elif job.keyId.startswith('surveys/'):
                jobClassName = 'RPATH_SurveyConcreteJob'
            else:
                jobClassName = 'CIM_ConcreteJob'
            jobInstanceId = self.createJobInstanceID(job.keyId)
            logInstanceId = self.createLogInstanceID(job.keyId)
            # We need to specify the namespace, otherwise sfcb segfaults.
            model['Dependent'] = pywbem.CIMInstanceName(
                classname=jobClassName,
                keybindings = dict(InstanceID = jobInstanceId),
                namespace = "root/cimv2")
            model['Antecedent'] = pywbem.CIMInstanceName(
                classname=logClassName,
                keybindings = dict(InstanceID = logInstanceId),
                namespace = "root/cimv2",
                )
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model, withCleanup=False)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise

    @classmethod
    def createLogInstanceID(cls, resourceId):
        return RPATH_RecordLog.RPATH_RecordLog.createInstanceID(resourceId)

    @classmethod
    def createJobInstanceID(cls, resourceId):
        return baseConcreteJobProvider.ConcreteJobMixIn.createInstanceID(resourceId)

def get_providers(env):
    rpath_useoflog_prov = RPATH_UseOfLog(env)
    return {'RPATH_UseOfLog': rpath_useoflog_prov}
