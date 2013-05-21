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


"""Python Provider for RPATH_LogEntry

Instruments the CIM class RPATH_LogEntry

"""

import inspect
import pywbem
from rpath_tools.lib import surveys
from pywbem.cim_provider2 import CIMProvider2

import stub_RPATH_SystemSurvey

stubClass = stub_RPATH_SystemSurvey.RPATH_SystemSurvey

class RPATH_SystemSurvey(stubClass):
    def __init__ (self, env):
        stubClass.__init__(self, env)
        self.surveyService = surveys.SurveyService()

    def get_instance(self, env, model):
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

        surveyId = self.fromInstanceID(model['InstanceID'])
        survey = self.surveyService.load(surveyId)
        model['Value'] = pywbem.CIMProperty('Value', survey.content,
                            type='string')


        # TODO fetch system resource matching the following keys:

        #model['Caption'] = '' # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElementName'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        #model['InstanceID'] = '' # TODO 
        #model['Name'] = '' # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        #model['Value'] = '' # TODO 
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
        model.path.update({'InstanceID': None})

        for survey in self.surveyService.list():
            model['InstanceID'] = self.createInstanceID(survey.id)
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise

    @classmethod
    def createInstanceID(cls, surveyId):
        return 'com.rpath:surveys/%s' % surveyId

    @classmethod
    def fromInstanceID(cls, instanceID):
        qualified = instanceID.split(':', 1)[-1]
        return qualified.rsplit('/', 1)[-1]

def get_providers(env):
    """
    Boilerplate provider registration function.
    Walk the module, find all subclasses of CIMProvider2 and return them
    """
    ret = {}
    for k, v in globals().items():
        if not inspect.isclass(v):
            continue
        if not issubclass(v, CIMProvider2) or v is CIMProvider2:
            continue
        prov = v(env)
        ret[k] = prov
    return ret
