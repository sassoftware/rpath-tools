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


"""Python Provider for RPATH_ComputerSystem

Instruments the CIM class RPATH_ComputerSystem

"""

import sys
import pywbem
from pywbem.cim_provider2 import CIMProvider2
import stub_RPATH_ComputerSystem

stubClass = stub_RPATH_ComputerSystem.RPATH_ComputerSystem

class RPATH_ComputerSystem(stubClass):
    ParentClassName = 'Linux_ComputerSystem'

    @staticmethod
    def updateInstance(instance):
        try:
            import helper_rpath_tools
        except ImportError:
            return

        a = helper_rpath_tools.Registration()
        instance['LocalUUID'] = a.localUuid
        instance['GeneratedUUID'] = a.generatedUuid

    def get_instance(self, env, model, instance=None):
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

        if instance is None:
            # not invoked via enum_instances, need to fetch the parent
            # instance
            ppath = model.path.__class__(self.ParentClassName,
                namespace = model.path.namespace,
                keybindings = dict(
                    Name = model.path['Name'],
                    CreationClassName = self.ParentClassName))
            instance = env.get_cimom_handle().GetInstance(ppath)
        model.path['CreationClassName'] = model.classname
        model.path['Name'] = instance.path['Name']
        instance.path = model.path
        instance.classname = model.classname
        instance['CreationClassName'] = model.classname
        self.updateInstance(instance)
        return instance

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
        model.path.update({'CreationClassName': model.classname, 'Name': None})

        ns = 'root/cimv2'
        if keys_only:
            method = env.get_cimom_handle().EnumerateInstanceNames
        else:
            method = env.get_cimom_handle().EnumerateInstances
        iterator = method(ns, self.ParentClassName)
        for inst in iterator:
            if keys_only:
                model.path = inst
                model.path.classname = model.classname
                model.path['CreationClassName'] = model.classname
                yield model
            else:
                yield self.get_instance(env, model, instance=inst)

    def cim_method_remoteregistration(self, env, object_name,
                                    param_managementnodeaddresses=None,
                                    param_requirednetwork=None,
                                    param_eventuuid=None):
        """Implements RPATH_ComputerSystem.RemoteRegistration()

        Remote Registration
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method RemoteRegistration() 
            should be invoked.
        param_managementnodeaddresses --  The input parameter ManagementNodeAddresses (type [unicode,]) 
            List of management nodes against this system will be registered
            

        Returns a two-tuple containing the return value (type pywbem.Uint16
        self.Values.RemoteRegistration) and a list of CIMParameter objects
        representing the output parameters

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
        logger.log_debug('Entering %s.cim_method_remoteregistration()' \
                % self.__class__.__name__)

        out_params = []
        rval = self.Values.RemoteRegistration.Failed

        try:
            import helper_rpath_tools
        except ImportError:
            return (rval, out_params)

        registration = helper_rpath_tools.Registration()
        registration.setManagementNodes(param_managementnodeaddresses)
        registration.setConaryProxy(param_managementnodeaddresses)
        registration.setRequiredNetwork(param_requirednetwork)
        a = helper_rpath_tools.Registration(event_uuid=param_eventuuid)
        try:
            a.run()
        except:
            exc = sys.exc_info()
            import traceback
            tb = ''.join(traceback.format_exception(*exc))
            errorSummary = "Error registering: %s" % exc[1]
            sys.stdout.write(tb)
            logger.log_error(errorSummary)
            logger.log_error("%s" % tb)
            out_params.append(pywbem.CIMParameter('errorSummary',
                type='string', value=errorSummary))
            out_params.append(pywbem.CIMParameter('errorDetails',
                type='string', value=tb))
            return (rval, out_params)

        rval = self.Values.RemoteRegistration.OK

        return (rval, out_params)

    def cim_method_updatemanagementconfiguration(self, env, object_name,
                                                 param_managementnodeaddresses=None,
                                                 param_requirednetwork=None):
        """Implements RPATH_ComputerSystem.UpdateManagementConfiguration()

        Update Management Configuration
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method UpdateManagementConfiguration() 
            should be invoked.
        param_managementnodeaddresses --  The input parameter ManagementNodeAddresses (type [unicode,]) 
            List of management nodes against this system will be registered
            
        param_requirednetwork --  The input parameter RequiredNetwork (type unicode) 
            The Managed System will advertise this IP address as the
            preferred one to be used when talking to it
            

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.UpdateManagementConfiguration)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        errorDetails -- (type unicode) 
            If the call failed, this string contains a detailed description
            of the error
            
        errorSummary -- (type unicode) 
            If the call failed, this string contains a short description of
            the error
            

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
        logger.log_debug('Entering %s.cim_method_updatemanagementconfiguration()' \
                % self.__class__.__name__)

        out_params = []
        rval = self.Values.UpdateManagementConfiguration.Failed

        try:
            import helper_rpath_tools
        except ImportError:
            return (rval, out_params)

        registration = helper_rpath_tools.Registration()
        registration.setManagementNodes(param_managementnodeaddresses)
        registration.setConaryProxy(param_managementnodeaddresses)
        registration.setRequiredNetwork(param_requirednetwork)
        rval = self.Values.RemoteRegistration.OK

        return (rval, out_params)

def get_providers(env): 
    rpath_computersystem_prov = RPATH_ComputerSystem(env)  
    return {'RPATH_ComputerSystem': rpath_computersystem_prov} 
