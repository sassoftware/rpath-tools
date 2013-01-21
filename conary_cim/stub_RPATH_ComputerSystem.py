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

import pywbem
from pywbem.cim_provider2 import CIMProvider2

class RPATH_ComputerSystem(CIMProvider2):
    """Instrument the CIM class RPATH_ComputerSystem 

    A class derived from System that is a special collection of
    ManagedSystemElements. This collection is related to the providing of
    compute capabilities and MAY serve as an aggregation point to
    associate one or more of the following elements: FileSystem,
    OperatingSystem, Processor and Memory (Volatile and/or NonVolatile
    Storage).
    
    """

    def __init__ (self, env):
        logger = env.get_logger()
        logger.log_debug('Initializing provider %s from %s' \
                % (self.__class__.__name__, __file__))

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
        #   model['CreationClassName']
        #   model['Name']

        #model['AvailableRequestedStates'] = [self.Values.AvailableRequestedStates.<VAL>,] # TODO 
        #model['Caption'] = '' # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        #model['Dedicated'] = [self.Values.Dedicated.<VAL>,] # TODO 
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElementName'] = '' # TODO 
        #model['EnabledDefault'] = self.Values.EnabledDefault.Enabled # TODO 
        #model['EnabledState'] = self.Values.EnabledState.Not_Applicable # TODO 
        #model['GeneratedUUID'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['IdentifyingDescriptions'] = ['',] # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        #model['InstanceID'] = '' # TODO 
        #model['LocalUUID'] = '' # TODO 
        #model['NameFormat'] = self.Values.NameFormat.<VAL> # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherDedicatedDescriptions'] = ['',] # TODO 
        #model['OtherEnabledState'] = '' # TODO 
        #model['OtherIdentifyingInfo'] = ['',] # TODO 
        #model['PowerManagementCapabilities'] = [self.Values.PowerManagementCapabilities.<VAL>,] # TODO 
        #model['PrimaryOwnerContact'] = '' # TODO 
        #model['PrimaryOwnerName'] = '' # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['RequestedState'] = self.Values.RequestedState.Not_Applicable # TODO 
        #model['ResetCapability'] = self.Values.ResetCapability.<VAL> # TODO 
        #model['Roles'] = ['',] # TODO 
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
        model.path.update({'CreationClassName': None, 'Name': None})
        
        while False: # TODO more instances?
            # TODO fetch system resource
            # Key properties    
            model['CreationClassName'] = 'RPATH_ComputerSystem'    
            #model['Name'] = '' # TODO (type = unicode)
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise

    def set_instance(self, env, instance, modify_existing):
        """Return a newly created or modified instance.

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        instance -- The new pywbem.CIMInstance.  If modifying an existing 
            instance, the properties on this instance have been filtered by 
            the PropertyList from the request.
        modify_existing -- True if ModifyInstance, False if CreateInstance

        Return the new instance.  The keys must be set on the new instance. 

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_NOT_SUPPORTED
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, unrecognized 
            or otherwise incorrect parameters)
        CIM_ERR_ALREADY_EXISTS (the CIM Instance already exists -- only 
            valid if modify_existing is False, indicating that the operation
            was CreateInstance)
        CIM_ERR_NOT_FOUND (the CIM Instance does not exist -- only valid 
            if modify_existing is True, indicating that the operation
            was ModifyInstance)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.set_instance()' \
                % self.__class__.__name__)
        # TODO create or modify the instance
        raise pywbem.CIMError(pywbem.CIM_ERR_NOT_SUPPORTED) # Remove to implement
        return instance

    def delete_instance(self, env, instance_name):
        """Delete an instance.

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        instance_name -- A pywbem.CIMInstanceName specifying the instance 
            to delete.

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_NOT_SUPPORTED
        CIM_ERR_INVALID_NAMESPACE
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, unrecognized 
            or otherwise incorrect parameters)
        CIM_ERR_INVALID_CLASS (the CIM Class does not exist in the specified 
            namespace)
        CIM_ERR_NOT_FOUND (the CIM Class does exist, but the requested CIM 
            Instance does not exist in the specified namespace)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """ 

        logger = env.get_logger()
        logger.log_debug('Entering %s.delete_instance()' \
                % self.__class__.__name__)

        # TODO delete the resource
        raise pywbem.CIMError(pywbem.CIM_ERR_NOT_SUPPORTED) # Remove to implement
        
    def cim_method_requeststatechange(self, env, object_name,
                                      param_requestedstate=None,
                                      param_timeoutperiod=None):
        """Implements RPATH_ComputerSystem.RequestStateChange()

        Requests that the state of the element be changed to the value
        specified in the RequestedState parameter. When the requested
        state change takes place, the EnabledState and RequestedState of
        the element will be the same. Invoking the RequestStateChange
        method multiple times could result in earlier requests being
        overwritten or lost. \nA return code of 0 shall indicate the state
        change was successfully initiated. \nA return code of 3 shall
        indicate that the state transition cannot complete within the
        interval specified by the TimeoutPeriod parameter. \nA return code
        of 4096 (0x1000) shall indicate the state change was successfully
        initiated, a ConcreteJob has been created, and its reference
        returned in the output parameter Job. Any other return code
        indicates an error condition.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method RequestStateChange() 
            should be invoked.
        param_requestedstate --  The input parameter RequestedState (type pywbem.Uint16 self.Values.RequestStateChange.RequestedState) 
            The state requested for the element. This information will be
            placed into the RequestedState property of the instance if the
            return code of the RequestStateChange method is 0 (\'Completed
            with No Error\'), or 4096 (0x1000) (\'Job Started\'). Refer to
            the description of the EnabledState and RequestedState
            properties for the detailed explanations of the RequestedState
            values.
            
        param_timeoutperiod --  The input parameter TimeoutPeriod (type pywbem.CIMDateTime) 
            A timeout period that specifies the maximum amount of time that
            the client expects the transition to the new state to take.
            The interval format must be used to specify the TimeoutPeriod.
            A value of 0 or a null parameter indicates that the client has
            no time requirements for the transition. \nIf this property
            does not contain 0 or null and the implementation does not
            support this parameter, a return code of \'Use Of Timeout
            Parameter Not Supported\' shall be returned.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.RequestStateChange)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Job -- (type REF (pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...)) 
            May contain a reference to the ConcreteJob created to track the
            state transition initiated by the method invocation.
            

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
        logger.log_debug('Entering %s.cim_method_requeststatechange()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.RequestStateChange)
        return (rval, out_params)
        
    def cim_method_setpowerstate(self, env, object_name,
                                 param_powerstate=None,
                                 param_time=None):
        """Implements RPATH_ComputerSystem.SetPowerState()

        Sets the power state of the computer. The use of this method has
        been deprecated. Instead, use the SetPowerState method in the
        associated PowerManagementService class.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method SetPowerState() 
            should be invoked.
        param_powerstate --  The input parameter PowerState (type pywbem.Uint32 self.Values.SetPowerState.PowerState) 
            The Desired state for the COmputerSystem.
            
        param_time --  The input parameter Time (type pywbem.CIMDateTime) 
            Time indicates when the power state should be set, either as a
            regular date-time value or as an interval value (where the
            interval begins when the method invocation is received.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
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
        logger.log_debug('Entering %s.cim_method_setpowerstate()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
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

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('errordetails', type='string', 
        #                   value='')] # TODO
        #out_params+= [pywbem.CIMParameter('errorsummary', type='string', 
        #                   value='')] # TODO
        #rval = # TODO (type pywbem.Uint16 self.Values.UpdateManagementConfiguration)
        return (rval, out_params)
        
    def cim_method_remoteregistration(self, env, object_name,
                                      param_managementnodeaddresses=None,
                                      param_eventuuid=None,
                                      param_requirednetwork=None):
        """Implements RPATH_ComputerSystem.RemoteRegistration()

        Remote Registration
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method RemoteRegistration() 
            should be invoked.
        param_managementnodeaddresses --  The input parameter ManagementNodeAddresses (type [unicode,]) 
            List of management nodes against this system will be registered
            
        param_eventuuid --  The input parameter EventUUID (type unicode) 
            Event UUID that originated this registration request
            
        param_requirednetwork --  The input parameter RequiredNetwork (type unicode) 
            The Managed System will advertise this IP address as the
            preferred one to be used when talking to it
            

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.RemoteRegistration)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        errorSummary -- (type unicode) 
            If the registration failed, this string contains a short
            description of the error
            
        errorDetails -- (type unicode) 
            If the registration failed, this string contains a detailed
            description of the error
            

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

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('errorsummary', type='string', 
        #                   value='')] # TODO
        #out_params+= [pywbem.CIMParameter('errordetails', type='string', 
        #                   value='')] # TODO
        #rval = # TODO (type pywbem.Uint16 self.Values.RemoteRegistration)
        return (rval, out_params)
        
    class Values(object):
        class DetailedStatus(object):
            Not_Available = pywbem.Uint16(0)
            No_Additional_Information = pywbem.Uint16(1)
            Stressed = pywbem.Uint16(2)
            Predictive_Failure = pywbem.Uint16(3)
            Non_Recoverable_Error = pywbem.Uint16(4)
            Supporting_Entity_in_Error = pywbem.Uint16(5)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..
            _reverse_map = {0: 'Not Available', 1: 'No Additional Information', 2: 'Stressed', 3: 'Predictive Failure', 4: 'Non-Recoverable Error', 5: 'Supporting Entity in Error'}

        class RequestedState(object):
            Unknown = pywbem.Uint16(0)
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Shut_Down = pywbem.Uint16(4)
            No_Change = pywbem.Uint16(5)
            Offline = pywbem.Uint16(6)
            Test = pywbem.Uint16(7)
            Deferred = pywbem.Uint16(8)
            Quiesce = pywbem.Uint16(9)
            Reboot = pywbem.Uint16(10)
            Reset = pywbem.Uint16(11)
            Not_Applicable = pywbem.Uint16(12)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 32768..65535
            _reverse_map = {0: 'Unknown', 2: 'Enabled', 3: 'Disabled', 4: 'Shut Down', 5: 'No Change', 6: 'Offline', 7: 'Test', 8: 'Deferred', 9: 'Quiesce', 10: 'Reboot', 11: 'Reset', 12: 'Not Applicable'}

        class HealthState(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(5)
            Degraded_Warning = pywbem.Uint16(10)
            Minor_failure = pywbem.Uint16(15)
            Major_failure = pywbem.Uint16(20)
            Critical_failure = pywbem.Uint16(25)
            Non_recoverable_error = pywbem.Uint16(30)
            # DMTF_Reserved = ..
            _reverse_map = {0: 'Unknown', 5: 'OK', 10: 'Degraded/Warning', 15: 'Minor failure', 20: 'Major failure', 25: 'Critical failure', 30: 'Non-recoverable error'}

        class SetPowerState(object):
            class PowerState(object):
                Full_Power = pywbem.Uint32(1)
                Power_Save___Low_Power_Mode = pywbem.Uint32(2)
                Power_Save___Standby = pywbem.Uint32(3)
                Power_Save___Other = pywbem.Uint32(4)
                Power_Cycle = pywbem.Uint32(5)
                Power_Off = pywbem.Uint32(6)
                Hibernate = pywbem.Uint32(7)
                Soft_Off = pywbem.Uint32(8)

        class TransitioningToState(object):
            Unknown = pywbem.Uint16(0)
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Shut_Down = pywbem.Uint16(4)
            No_Change = pywbem.Uint16(5)
            Offline = pywbem.Uint16(6)
            Test = pywbem.Uint16(7)
            Defer = pywbem.Uint16(8)
            Quiesce = pywbem.Uint16(9)
            Reboot = pywbem.Uint16(10)
            Reset = pywbem.Uint16(11)
            Not_Applicable = pywbem.Uint16(12)
            # DMTF_Reserved = ..
            _reverse_map = {0: 'Unknown', 2: 'Enabled', 3: 'Disabled', 4: 'Shut Down', 5: 'No Change', 6: 'Offline', 7: 'Test', 8: 'Defer', 9: 'Quiesce', 10: 'Reboot', 11: 'Reset', 12: 'Not Applicable'}

        class EnabledDefault(object):
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Not_Applicable = pywbem.Uint16(5)
            Enabled_but_Offline = pywbem.Uint16(6)
            No_Default = pywbem.Uint16(7)
            Quiesce = pywbem.Uint16(9)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 32768..65535
            _reverse_map = {2: 'Enabled', 3: 'Disabled', 5: 'Not Applicable', 6: 'Enabled but Offline', 7: 'No Default', 9: 'Quiesce'}

        class AvailableRequestedStates(object):
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Shut_Down = pywbem.Uint16(4)
            Offline = pywbem.Uint16(6)
            Test = pywbem.Uint16(7)
            Defer = pywbem.Uint16(8)
            Quiesce = pywbem.Uint16(9)
            Reboot = pywbem.Uint16(10)
            Reset = pywbem.Uint16(11)
            # DMTF_Reserved = ..
            _reverse_map = {2: 'Enabled', 3: 'Disabled', 4: 'Shut Down', 6: 'Offline', 7: 'Test', 8: 'Defer', 9: 'Quiesce', 10: 'Reboot', 11: 'Reset'}

        class EnabledState(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Shutting_Down = pywbem.Uint16(4)
            Not_Applicable = pywbem.Uint16(5)
            Enabled_but_Offline = pywbem.Uint16(6)
            In_Test = pywbem.Uint16(7)
            Deferred = pywbem.Uint16(8)
            Quiesce = pywbem.Uint16(9)
            Starting = pywbem.Uint16(10)
            # DMTF_Reserved = 11..32767
            # Vendor_Reserved = 32768..65535
            _reverse_map = {0: 'Unknown', 1: 'Other', 2: 'Enabled', 3: 'Disabled', 4: 'Shutting Down', 5: 'Not Applicable', 6: 'Enabled but Offline', 7: 'In Test', 8: 'Deferred', 9: 'Quiesce', 10: 'Starting'}

        class RemoteRegistration(object):
            OK = pywbem.Uint16(0)
            Failed = pywbem.Uint16(1)

        class ResetCapability(object):
            Other = pywbem.Uint16(1)
            Unknown = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Enabled = pywbem.Uint16(4)
            Not_Implemented = pywbem.Uint16(5)
            _reverse_map = {1: 'Other', 2: 'Unknown', 3: 'Disabled', 4: 'Enabled', 5: 'Not Implemented'}

        class Dedicated(object):
            Not_Dedicated = pywbem.Uint16(0)
            Unknown = pywbem.Uint16(1)
            Other = pywbem.Uint16(2)
            Storage = pywbem.Uint16(3)
            Router = pywbem.Uint16(4)
            Switch = pywbem.Uint16(5)
            Layer_3_Switch = pywbem.Uint16(6)
            Central_Office_Switch = pywbem.Uint16(7)
            Hub = pywbem.Uint16(8)
            Access_Server = pywbem.Uint16(9)
            Firewall = pywbem.Uint16(10)
            Print = pywbem.Uint16(11)
            I_O = pywbem.Uint16(12)
            Web_Caching = pywbem.Uint16(13)
            Management = pywbem.Uint16(14)
            Block_Server = pywbem.Uint16(15)
            File_Server = pywbem.Uint16(16)
            Mobile_User_Device = pywbem.Uint16(17)
            Repeater = pywbem.Uint16(18)
            Bridge_Extender = pywbem.Uint16(19)
            Gateway = pywbem.Uint16(20)
            Storage_Virtualizer = pywbem.Uint16(21)
            Media_Library = pywbem.Uint16(22)
            ExtenderNode = pywbem.Uint16(23)
            NAS_Head = pywbem.Uint16(24)
            Self_contained_NAS = pywbem.Uint16(25)
            UPS = pywbem.Uint16(26)
            IP_Phone = pywbem.Uint16(27)
            Management_Controller = pywbem.Uint16(28)
            Chassis_Manager = pywbem.Uint16(29)
            Host_based_RAID_controller = pywbem.Uint16(30)
            Storage_Device_Enclosure = pywbem.Uint16(31)
            Desktop = pywbem.Uint16(32)
            Laptop = pywbem.Uint16(33)
            Virtual_Tape_Library = pywbem.Uint16(34)
            Virtual_Library_System = pywbem.Uint16(35)
            Network_PC_Thin_Client = pywbem.Uint16(36)
            FC_Switch = pywbem.Uint16(37)
            Ethernet_Switch = pywbem.Uint16(38)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 32568..65535
            _reverse_map = {0: 'Not Dedicated', 1: 'Unknown', 2: 'Other', 3: 'Storage', 4: 'Router', 5: 'Switch', 6: 'Layer 3 Switch', 7: 'Central Office Switch', 8: 'Hub', 9: 'Access Server', 10: 'Firewall', 11: 'Print', 12: 'I/O', 13: 'Web Caching', 14: 'Management', 15: 'Block Server', 16: 'File Server', 17: 'Mobile User Device', 18: 'Repeater', 19: 'Bridge/Extender', 20: 'Gateway', 21: 'Storage Virtualizer', 22: 'Media Library', 23: 'ExtenderNode', 24: 'NAS Head', 25: 'Self-contained NAS', 26: 'UPS', 27: 'IP Phone', 28: 'Management Controller', 29: 'Chassis Manager', 30: 'Host-based RAID controller', 31: 'Storage Device Enclosure', 32: 'Desktop', 33: 'Laptop', 34: 'Virtual Tape Library', 35: 'Virtual Library System', 36: 'Network PC/Thin Client', 37: 'FC Switch', 38: 'Ethernet Switch'}

        class NameFormat(object):
            Other = 'Other'
            IP = 'IP'
            Dial = 'Dial'
            HID = 'HID'
            NWA = 'NWA'
            HWA = 'HWA'
            X25 = 'X25'
            ISDN = 'ISDN'
            IPX = 'IPX'
            DCC = 'DCC'
            ICD = 'ICD'
            E_164 = 'E.164'
            SNA = 'SNA'
            OID_OSI = 'OID/OSI'
            WWN = 'WWN'
            NAA = 'NAA'

        class Status(object):
            OK = 'OK'
            Error = 'Error'
            Degraded = 'Degraded'
            Unknown = 'Unknown'
            Pred_Fail = 'Pred Fail'
            Starting = 'Starting'
            Stopping = 'Stopping'
            Service = 'Service'
            Stressed = 'Stressed'
            NonRecover = 'NonRecover'
            No_Contact = 'No Contact'
            Lost_Comm = 'Lost Comm'
            Stopped = 'Stopped'

        class CommunicationStatus(object):
            Unknown = pywbem.Uint16(0)
            Not_Available = pywbem.Uint16(1)
            Communication_OK = pywbem.Uint16(2)
            Lost_Communication = pywbem.Uint16(3)
            No_Contact = pywbem.Uint16(4)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..
            _reverse_map = {0: 'Unknown', 1: 'Not Available', 2: 'Communication OK', 3: 'Lost Communication', 4: 'No Contact'}

        class OperationalStatus(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            OK = pywbem.Uint16(2)
            Degraded = pywbem.Uint16(3)
            Stressed = pywbem.Uint16(4)
            Predictive_Failure = pywbem.Uint16(5)
            Error = pywbem.Uint16(6)
            Non_Recoverable_Error = pywbem.Uint16(7)
            Starting = pywbem.Uint16(8)
            Stopping = pywbem.Uint16(9)
            Stopped = pywbem.Uint16(10)
            In_Service = pywbem.Uint16(11)
            No_Contact = pywbem.Uint16(12)
            Lost_Communication = pywbem.Uint16(13)
            Aborted = pywbem.Uint16(14)
            Dormant = pywbem.Uint16(15)
            Supporting_Entity_in_Error = pywbem.Uint16(16)
            Completed = pywbem.Uint16(17)
            Power_Mode = pywbem.Uint16(18)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..
            _reverse_map = {0: 'Unknown', 1: 'Other', 2: 'OK', 3: 'Degraded', 4: 'Stressed', 5: 'Predictive Failure', 6: 'Error', 7: 'Non-Recoverable Error', 8: 'Starting', 9: 'Stopping', 10: 'Stopped', 11: 'In Service', 12: 'No Contact', 13: 'Lost Communication', 14: 'Aborted', 15: 'Dormant', 16: 'Supporting Entity in Error', 17: 'Completed', 18: 'Power Mode'}

        class OperatingStatus(object):
            Unknown = pywbem.Uint16(0)
            Not_Available = pywbem.Uint16(1)
            Servicing = pywbem.Uint16(2)
            Starting = pywbem.Uint16(3)
            Stopping = pywbem.Uint16(4)
            Stopped = pywbem.Uint16(5)
            Aborted = pywbem.Uint16(6)
            Dormant = pywbem.Uint16(7)
            Completed = pywbem.Uint16(8)
            Migrating = pywbem.Uint16(9)
            Emigrating = pywbem.Uint16(10)
            Immigrating = pywbem.Uint16(11)
            Snapshotting = pywbem.Uint16(12)
            Shutting_Down = pywbem.Uint16(13)
            In_Test = pywbem.Uint16(14)
            Transitioning = pywbem.Uint16(15)
            In_Service = pywbem.Uint16(16)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..
            _reverse_map = {0: 'Unknown', 1: 'Not Available', 2: 'Servicing', 3: 'Starting', 4: 'Stopping', 5: 'Stopped', 6: 'Aborted', 7: 'Dormant', 8: 'Completed', 9: 'Migrating', 10: 'Emigrating', 11: 'Immigrating', 12: 'Snapshotting', 13: 'Shutting Down', 14: 'In Test', 15: 'Transitioning', 16: 'In Service'}

        class UpdateManagementConfiguration(object):
            OK = pywbem.Uint16(0)
            Failed = pywbem.Uint16(1)

        class PowerManagementCapabilities(object):
            Unknown = pywbem.Uint16(0)
            Not_Supported = pywbem.Uint16(1)
            Disabled = pywbem.Uint16(2)
            Enabled = pywbem.Uint16(3)
            Power_Saving_Modes_Entered_Automatically = pywbem.Uint16(4)
            Power_State_Settable = pywbem.Uint16(5)
            Power_Cycling_Supported = pywbem.Uint16(6)
            Timed_Power_On_Supported = pywbem.Uint16(7)
            _reverse_map = {0: 'Unknown', 1: 'Not Supported', 2: 'Disabled', 3: 'Enabled', 4: 'Power Saving Modes Entered Automatically', 5: 'Power State Settable', 6: 'Power Cycling Supported', 7: 'Timed Power On Supported'}

        class RequestStateChange(object):
            Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unknown_or_Unspecified_Error = pywbem.Uint32(2)
            Cannot_complete_within_Timeout_Period = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Invalid_State_Transition = pywbem.Uint32(4097)
            Use_of_Timeout_Parameter_Not_Supported = pywbem.Uint32(4098)
            Busy = pywbem.Uint32(4099)
            # Method_Reserved = 4100..32767
            # Vendor_Specific = 32768..65535
            class RequestedState(object):
                Enabled = pywbem.Uint16(2)
                Disabled = pywbem.Uint16(3)
                Shut_Down = pywbem.Uint16(4)
                Offline = pywbem.Uint16(6)
                Test = pywbem.Uint16(7)
                Defer = pywbem.Uint16(8)
                Quiesce = pywbem.Uint16(9)
                Reboot = pywbem.Uint16(10)
                Reset = pywbem.Uint16(11)
                # DMTF_Reserved = ..
                # Vendor_Reserved = 32768..65535

        class PrimaryStatus(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(1)
            Degraded = pywbem.Uint16(2)
            Error = pywbem.Uint16(3)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..
            _reverse_map = {0: 'Unknown', 1: 'OK', 2: 'Degraded', 3: 'Error'}

## end of class RPATH_ComputerSystemProvider
    
## get_providers() for associating CIM Class Name to python provider class name
    
def get_providers(env): 
    rpath_computersystem_prov = RPATH_ComputerSystem(env)  
    return {'RPATH_ComputerSystem': rpath_computersystem_prov} 
