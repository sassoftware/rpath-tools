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


"""Python Provider for RPATH_SoftwareInstallationService

Instruments the CIM class RPATH_SoftwareInstallationService

"""

import inspect
import pywbem
from pywbem.cim_provider2 import CIMProvider2

from mixin_computersystem import MixInComputerSystem
import stub_RPATH_SystemSurveyService

from rpath_tools.lib import jobs
import RPATH_SurveyConcreteJob

stubClass = stub_RPATH_SystemSurveyService.RPATH_SystemSurveyService

class RPATH_SystemSurveyService(stubClass, MixInComputerSystem):
    """Instrument the CIM class RPATH_SoftwareInstallationService

    A subclass of service which provides methods to install (or update)
    Software Identities in ManagedElements.
    
    """

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

        # TODO fetch system resource matching the following keys:
        #   model['SystemName']
        #   model['SystemCreationClassName']
        #   model['CreationClassName']
        #   model['Name']

        #model['AvailableRequestedStates'] = [self.Values.AvailableRequestedStates.<VAL>,] # TODO 
        #model['Caption'] = '' # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElementName'] = '' # TODO 
        #model['EnabledDefault'] = self.Values.EnabledDefault.Enabled # TODO 
        #model['EnabledState'] = self.Values.EnabledState.Not_Applicable # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        #model['InstanceID'] = '' # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherEnabledState'] = '' # TODO 
        #model['PrimaryOwnerContact'] = '' # TODO 
        #model['PrimaryOwnerName'] = '' # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['RequestedState'] = self.Values.RequestedState.Not_Applicable # TODO 
        #model['Started'] = bool() # TODO 
        #model['StartMode'] = self.Values.StartMode.<VAL> # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        #model['TimeOfLastStateChange'] = pywbem.CIMDateTime() # TODO 
        #model['TransitioningToState'] = self.Values.TransitioningToState.Not_Applicable # TODO 
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
        model.path.update({'CreationClassName': None, 'SystemName': None,
            'Name': None, 'SystemCreationClassName': None})

        systemCreationClassName, systemName = self.getComputerSystemName(env)

        while True:
            # Key properties
            model['SystemName'] = systemName
            model['SystemCreationClassName'] = systemCreationClassName
            model['CreationClassName'] = self.__class__.__name__
            model['Name'] = 'rPath System Survey Service'
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise
            # We can only produce one instance of this object
            break

    def cim_method_scan(self, env, object_name,
                        param_systemmodel=None,
                        param_desiredpackages=None):
        """Implements RPATH_SystemSurveyService.Scan()

        Check for updates
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method Scan() 
            should be invoked.
        param_systemmodel --  The input parameter SystemModel (type [unicode,]) 
            A system model against which a preview will be computed. Takes
            precedence over DesiredPackages
            
        param_desiredpackages --  The input parameter DesiredPackages (type [unicode,]) 
            A list of packages against which a preview will be computed
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.Scan)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Job -- (type REF (pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...)) 
            Reference to the job (may be null if job completed).
            

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
        logger.log_debug('Entering %s.cim_method_scan()' \
                % self.__class__.__name__)

        # Create update job
        task = jobs.SurveyTask().new()
        task(param_desiredpackages, param_systemmodel)

        jobInstanceID = RPATH_SurveyConcreteJob.RPATH_SurveyConcreteJob.createInstanceID(task.get_job_id())
        job = pywbem.CIMInstanceName(classname='RPATH_SurveyConcreteJob',
            keybindings = dict(InstanceID = jobInstanceID),
            namespace = "root/cimv2")

        out_params = []
        out_params.append(pywbem.CIMParameter('job', type='reference',
                      value=job))
        rval = self.Values.Scan.Method_Parameters_Checked___Job_Started
        return (rval, out_params)


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
