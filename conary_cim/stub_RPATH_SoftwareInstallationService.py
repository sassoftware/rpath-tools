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

import pywbem
from pywbem.cim_provider2 import CIMProvider2

class RPATH_SoftwareInstallationService(CIMProvider2):
    """Instrument the CIM class RPATH_SoftwareInstallationService 

    A subclass of service which provides methods to install (or update)
    Software Identities in ManagedElements.
    
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
        #   model['SystemName']
        #   model['SystemCreationClassName']
        #   model['CreationClassName']
        #   model['Name']

        #model['AutomaticUpdates'] = self.Values.AutomaticUpdates.<VAL> # TODO 
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
        #model['ProxyServerAddress'] = '' # TODO 
        #model['RepositoryAddress'] = '' # TODO 
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
        
        while False: # TODO more instances?
            # TODO fetch system resource
            # Key properties    
            #model['SystemName'] = '' # TODO (type = unicode)    
            #model['SystemCreationClassName'] = '' # TODO (type = unicode)    
            model['CreationClassName'] = 'RPATH_SoftwareInstallationService'    
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
        """Implements RPATH_SoftwareInstallationService.RequestStateChange()

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
        
    def cim_method_stopservice(self, env, object_name):
        """Implements RPATH_SoftwareInstallationService.StopService()

        The StopService method places the Service in the stopped state.
        Note that the function of this method overlaps with the
        RequestedState property. RequestedState was added to the model to
        maintain a record (such as a persisted value) of the last state
        request. Invoking the StopService method should set the
        RequestedState property appropriately. The method returns an
        integer value of 0 if the Service was successfully stopped, 1 if
        the request is not supported, and any other number to indicate an
        error. In a subclass, the set of possible return codes could be
        specified using a ValueMap qualifier on the method. The strings to
        which the ValueMap contents are translated can also be specified
        in the subclass as a Values array qualifier. \n\nNote: The
        semantics of this method overlap with the RequestStateChange
        method that is inherited from EnabledLogicalElement. This method
        is maintained because it has been widely implemented, and its
        simple "stop" semantics are convenient to use.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method StopService() 
            should be invoked.

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
        logger.log_debug('Entering %s.cim_method_stopservice()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_installfromuri(self, env, object_name,
                                  param_installoptionsvalues=None,
                                  param_uri=None,
                                  param_installoptions=None,
                                  param_target=None):
        """Implements RPATH_SoftwareInstallationService.InstallFromURI()

        Start a job to install software from a specific URI in a
        ManagedElement. \nNote that this method is provided to support
        existing, alternative download mechanisms (such as used for
        firmware download). The \'normal\' mechanism will be to use the
        InstallFromSoftwareIdentity method.\nIf 0 is returned, the
        function completed successfully and no ConcreteJob instance was
        required. If 4096/0x1000 is returned, a ConcreteJob will be
        started to to perform the install. The Job\'s reference will be
        returned in the output parameter Job.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method InstallFromURI() 
            should be invoked.
        param_installoptionsvalues --  The input parameter InstallOptionsValues (type [unicode,]) 
            InstallOptionsValues is an array of strings providing
            additionalinformation to InstallOptions for the method to
            install the software. Each entry of this array is related to
            the entry in InstallOptions that is located at the same index
            providing additional information for InstallOptions. \nFor
            further information on the use of InstallOptionsValues
            parameter, see the description of the InstallOptionsValues
            parameter of the
            SoftwareInstallationService.InstallFromSoftwareIdentity
            method.
            
        param_uri --  The input parameter URI (type unicode) 
            A URI for the software based on RFC 2079.
            
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.InstallFromURI.InstallOptions) 
            Options to control the install process. \nSee the
            InstallOptions parameter of the
            SoftwareInstallationService.InstallFromSoftwareIdentity method
            for the description of these values.
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.InstallFromURI)
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
        logger.log_debug('Entering %s.cim_method_installfromuri()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.InstallFromURI)
        return (rval, out_params)
        
    def cim_method_checksoftwareidentity(self, env, object_name,
                                         param_source=None,
                                         param_target=None,
                                         param_collection=None):
        """Implements RPATH_SoftwareInstallationService.CheckSoftwareIdentity()

        This method allows a client application to determine whether a
        specific SoftwareIdentity can be installed (or updated) on a
        ManagedElement. It also allows other characteristics to be
        determined such as whether install will require a reboot. In
        addition a client can check whether the SoftwareIdentity can be
        added simulataneously to a specified SofwareIndentityCollection. A
        client MAY specify either or both of the Collection and Target
        parameters. The Collection parameter is only supported if
        SoftwareInstallationServiceCapabilities.CanAddToCollection is
        TRUE.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method CheckSoftwareIdentity() 
            should be invoked.
        param_source --  The input parameter Source (type REF (pywbem.CIMInstanceName(classname='CIM_SoftwareIdentity', ...)) 
            Reference to the SoftwareIdentity to be checked.
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            Reference to the ManagedElement that the Software Identity is
            going to be installed in (or updated).
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_Collection', ...)) 
            Reference to the Collection to which the Software Identity will
            be added.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.CheckSoftwareIdentity)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        InstallCharacteristics -- (type [pywbem.Uint16,] self.Values.CheckSoftwareIdentity.InstallCharacteristics) 
            The parameter describes the characteristics of the
            installation/update that will take place if the Source
            Software Identity is installed: \nTarget automatic reset: The
            target element will automatically reset once the installation
            is complete. \nSystem automatic reset: The containing system
            of the target ManagedElement (normally a logical device or the
            system itself) will automatically reset/reboot once the
            installation is complete. \nSeparate target reset required:
            EnabledLogicalElement.RequestStateChange MUST be used to reset
            the target element after the SoftwareIdentity is installed.
            \nSeparate system reset required:
            EnabledLogicalElement.RequestStateChange MUST be used to
            reset/reboot the containing system of the target
            ManagedElement after the SoftwareIdentity is installed.
            \nManual Reboot Required: The system MUST be manually rebooted
            by the user. \nNo reboot required : No reboot is required
            after installation. \nUser Intervention Recomended : It is
            recommended that a user confirm installation of this
            SoftwareIdentity. Inappropriate application MAY have serious
            consequences. \nMAY be added to specified collection : The
            SoftwareIndentity MAY be added to specified Collection.
            

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
        logger.log_debug('Entering %s.cim_method_checksoftwareidentity()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('installcharacteristics', type='uint16', 
        #                   value=[self.Values.CheckSoftwareIdentity.InstallCharacteristics.<VAL>,])] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.CheckSoftwareIdentity)
        return (rval, out_params)
        
    def cim_method_changeaffectedelementsassignedsequence(self, env, object_name,
                                                          param_managedelements,
                                                          param_assignedsequence):
        """Implements RPATH_SoftwareInstallationService.ChangeAffectedElementsAssignedSequence()

        This method is called to change relative sequence in which order
        the ManagedElements associated to the Service through
        CIM_ServiceAffectsElement association are affected. In the case
        when the Service represents an interface for client to execute
        extrinsic methods and when it is used for grouping of the managed
        elements that could be affected, the ordering represents the
        relevant priority of the affected managed elements with respect to
        each other. \nAn ordered array of ManagedElement instances is
        passed to this method, where each ManagedElement instance shall be
        already be associated with this Service instance via
        CIM_ServiceAffectsElement association. If one of the
        ManagedElements is not associated to the Service through
        CIM_ServiceAffectsElement association, the implementation shall
        return a value of 2 ("Error Occured"). \nUpon successful execution
        of this method, if the AssignedSequence parameter is NULL, the
        value of the AssignedSequence property on each instance of
        CIM_ServiceAffectsElement shall be updated such that the values of
        AssignedSequence properties shall be monotonically increasing in
        correlation with the position of the referenced ManagedElement
        instance in the ManagedElements input parameter. That is, the
        first position in the array shall have the lowest value for
        AssignedSequence. The second position shall have the second lowest
        value, and so on. Upon successful execution, if the
        AssignedSequence parameter is not NULL, the value of the
        AssignedSequence property of each instance of
        CIM_ServiceAffectsElement referencing the ManagedElement instance
        in the ManagedElements array shall be assigned the value of the
        corresponding index of the AssignedSequence parameter array. For
        ManagedElements instances which are associated with the Service
        instance via CIM_ServiceAffectsElement and are not present in the
        ManagedElements parameter array, the AssignedSequence property on
        the CIM_ServiceAffects association shall be assigned a value of 0.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ChangeAffectedElementsAssignedSequence() 
            should be invoked.
        param_managedelements --  The input parameter ManagedElements (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) (Required)
            An array of ManagedElements.
            
        param_assignedsequence --  The input parameter AssignedSequence (type [pywbem.Uint16,]) (Required)
            An array of integers representing AssignedSequence for the
            ManagedElement in the corresponding index of the
            ManagedElements parameter.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.ChangeAffectedElementsAssignedSequence)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Job -- (type REF (pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...)) 
            Reference to the job spawned if the operation continues after
            the method returns. (May be null if the task is completed).
            

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
        logger.log_debug('Entering %s.cim_method_changeaffectedelementsassignedsequence()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.ChangeAffectedElementsAssignedSequence)
        return (rval, out_params)
        
    def cim_method_setrepositoryaddress(self, env, object_name,
                                        param_repositoryaddress=None):
        """Implements RPATH_SoftwareInstallationService.SetRepositoryAddress()

        Set Repository Address
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method SetRepositoryAddress() 
            should be invoked.
        param_repositoryaddress --  The input parameter RepositoryAddress (type unicode) 

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.SetRepositoryAddress)
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
        logger.log_debug('Entering %s.cim_method_setrepositoryaddress()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint16 self.Values.SetRepositoryAddress)
        return (rval, out_params)
        
    def cim_method_updatefromsystemmodel(self, env, object_name,
                                         param_managementnodeaddresses=None,
                                         param_systemmodel=None,
                                         param_installoptions=None,
                                         param_target=None):
        """Implements RPATH_SoftwareInstallationService.UpdateFromSystemModel()

        Start a job to synchronize software ManagedElement (Target),based
        on a system model.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method UpdateFromSystemModel() 
            should be invoked.
        param_managementnodeaddresses --  The input parameter ManagementNodeAddresses (type [unicode,]) 
            List of management nodes against this system will be registered
            
        param_systemmodel --  The input parameter SystemModel (type unicode) 
            System model
            
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.UpdateFromSystemModel.InstallOptions) 
            Installation options
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.UpdateFromSystemModel)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Job -- (type REF (pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob', ...)) 
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
        logger.log_debug('Entering %s.cim_method_updatefromsystemmodel()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.UpdateFromSystemModel)
        return (rval, out_params)
        
    def cim_method_setautomaticupdates(self, env, object_name,
                                       param_automaticupdates=None):
        """Implements RPATH_SoftwareInstallationService.SetAutomaticUpdates()

        Set automatic updates
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method SetAutomaticUpdates() 
            should be invoked.
        param_automaticupdates --  The input parameter AutomaticUpdates (type pywbem.Uint16 self.Values.SetAutomaticUpdates.AutomaticUpdates) 
            Automatic updates setting
            

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.SetAutomaticUpdates)
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
        logger.log_debug('Entering %s.cim_method_setautomaticupdates()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint16 self.Values.SetAutomaticUpdates)
        return (rval, out_params)
        
    def cim_method_installfromsoftwareidentity(self, env, object_name,
                                               param_installoptions=None,
                                               param_target=None,
                                               param_collection=None,
                                               param_source=None,
                                               param_installoptionsvalues=None):
        """Implements RPATH_SoftwareInstallationService.InstallFromSoftwareIdentity()

        Start a job to install or update a SoftwareIdentity (Source) on a
        ManagedElement (Target). \nIn addition the method can be used to
        add the SoftwareIdentity simulataneously to a specified
        SofwareIndentityCollection. A client MAY specify either or both of
        the Collection and Target parameters. The Collection parameter is
        only supported if SoftwareInstallationService.CanAddToCollection
        is TRUE. \nIf 0 is returned, the function completed successfully
        and no ConcreteJob instance was required. If 4096/0x1000 is
        returned, a ConcreteJob will be started to perform the install.
        The Job\'s reference will be returned in the output parameter Job.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method InstallFromSoftwareIdentity() 
            should be invoked.
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.InstallFromSoftwareIdentity.InstallOptions) 
            Options to control the install process.\nDefer target/system
            reset : do not automatically reset the target/system.\nForce
            installation : Force the installation of the same or an older
            SoftwareIdentity. Install: Perform an installation of this
            software on the managed element.\nUpdate: Perform an update of
            this software on the managed element.\nRepair: Perform a
            repair of the installation of this software on the managed
            element by forcing all the files required for installing the
            software to be reinstalled.\nReboot: Reboot or reset the
            system immediately after the install or update of this
            software, if the install or the update requires a reboot or
            reset.\nPassword: Password will be specified as clear text
            without any encryption for performing the install or
            update.\nUninstall: Uninstall the software on the managed
            element.\nLog: Create a log for the install or update of the
            software.\nSilentMode: Perform the install or update without
            displaying any user interface.\nAdministrativeMode: Perform
            the install or update of the software in the administrative
            mode. ScheduleInstallAt: Indicates the time at which
            theinstall or update of the software will occur.
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target. If NULL then the SOftwareIdentity will
            be added to Collection only. The underlying implementation is
            expected to be able to obtain any necessary metadata from the
            Software Identity.
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_Collection', ...)) 
            Reference to the Collection to which the Software Identity
            SHALL be added. If NULL then the SOftware Identity will not be
            added to a Collection.
            
        param_source --  The input parameter Source (type REF (pywbem.CIMInstanceName(classname='CIM_SoftwareIdentity', ...)) 
            Reference to the source of the install.
            
        param_installoptionsvalues --  The input parameter InstallOptionsValues (type [unicode,]) 
            InstallOptionsValues is an array of strings providing
            additional information to InstallOptions for the method to
            install the software. Each entry of this array is related to
            the entry in InstallOptions that is located at the same index
            providing additional information for InstallOptions. \nIf the
            index in InstallOptions has the value "Password " then a value
            at the corresponding index of InstallOptionValues shall not be
            NULL. \nIf the index in InstallOptions has the value
            "ScheduleInstallAt" then the value at the corresponding index
            of InstallOptionValues shall not be NULL and shall be in the
            datetime type format. \nIf the index in InstallOptions has the
            value "Log " then a value at the corresponding index of
            InstallOptionValues may be NULL. \nIf the index in
            InstallOptions has the value "Defer target/system reset",
            "Force installation","Install", "Update", "Repair" or "Reboot"
            then a value at the corresponding index of InstallOptionValues
            shall be NULL.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.InstallFromSoftwareIdentity)
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
        logger.log_debug('Entering %s.cim_method_installfromsoftwareidentity()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.InstallFromSoftwareIdentity)
        return (rval, out_params)
        
    def cim_method_installfromnetworklocations(self, env, object_name,
                                               param_managementnodeaddresses=None,
                                               param_installoptions=None,
                                               param_target=None,
                                               param_installoptionvalues=None,
                                               param_sources=None):
        """Implements RPATH_SoftwareInstallationService.InstallFromNetworkLocations()

        Start a job to update or migrate software on a ManagedElement
        (Target).
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method InstallFromNetworkLocations() 
            should be invoked.
        param_managementnodeaddresses --  The input parameter ManagementNodeAddresses (type [unicode,]) 
            List of management nodes against this system will be registered
            
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.InstallFromNetworkLocations.InstallOptions) 
            Installation options
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target.
            
        param_installoptionvalues --  The input parameter InstallOptionValues (type [unicode,]) 
            Installation option values
            
        param_sources --  The input parameter Sources (type [unicode,]) 
            References to the locations
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.InstallFromNetworkLocations)
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
        logger.log_debug('Entering %s.cim_method_installfromnetworklocations()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.InstallFromNetworkLocations)
        return (rval, out_params)
        
    def cim_method_setproxyserveraddress(self, env, object_name,
                                         param_proxyserveraddress=None):
        """Implements RPATH_SoftwareInstallationService.SetProxyServerAddress()

        Set Proxy Server Address
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method SetProxyServerAddress() 
            should be invoked.
        param_proxyserveraddress --  The input parameter ProxyServerAddress (type unicode) 

        Returns a two-tuple containing the return value (type pywbem.Uint16 self.Values.SetProxyServerAddress)
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
        logger.log_debug('Entering %s.cim_method_setproxyserveraddress()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint16 self.Values.SetProxyServerAddress)
        return (rval, out_params)
        
    def cim_method_startservice(self, env, object_name):
        """Implements RPATH_SoftwareInstallationService.StartService()

        The StartService method places the Service in the started state.
        Note that the function of this method overlaps with the
        RequestedState property. RequestedState was added to the model to
        maintain a record (such as a persisted value) of the last state
        request. Invoking the StartService method should set the
        RequestedState property appropriately. The method returns an
        integer value of 0 if the Service was successfully started, 1 if
        the request is not supported, and any other number to indicate an
        error. In a subclass, the set of possible return codes could be
        specified using a ValueMap qualifier on the method. The strings to
        which the ValueMap contents are translated can also be specified
        in the subclass as a Values array qualifier. \n\nNote: The
        semantics of this method overlap with the RequestStateChange
        method that is inherited from EnabledLogicalElement. This method
        is maintained because it has been widely implemented, and its
        simple "start" semantics are convenient to use.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method StartService() 
            should be invoked.

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
        logger.log_debug('Entering %s.cim_method_startservice()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_checkavailableupdates(self, env, object_name,
                                         param_target=None):
        """Implements RPATH_SoftwareInstallationService.CheckAvailableUpdates()

        Check for updates
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method CheckAvailableUpdates() 
            should be invoked.
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            Reference to the ManagedElement that the Software Identity is
            going to be installed in (or updated).
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.CheckAvailableUpdates)
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
        logger.log_debug('Entering %s.cim_method_checkavailableupdates()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.CheckAvailableUpdates)
        return (rval, out_params)
        
    def cim_method_installfrombytestream(self, env, object_name,
                                         param_installoptionsvalues=None,
                                         param_image=None,
                                         param_installoptions=None,
                                         param_target=None):
        """Implements RPATH_SoftwareInstallationService.InstallFromByteStream()

        Start a job to download a series of bytes containing a software
        image to a ManagedElement. \nNote that this method is provided to
        support existing, alternative download mechanisms (such as used
        for firmware download). The \'normal\' mechanism will be to use
        the InstallFromSoftwareIdentity method. \nIf 0 is returned, the
        function completed successfully and no ConcreteJob instance was
        required. If 4096/0x1000 is returned, a ConcreteJob will be
        started to to perform the install. The Job\'s reference will be
        returned in the output parameter Job.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method InstallFromByteStream() 
            should be invoked.
        param_installoptionsvalues --  The input parameter InstallOptionsValues (type [unicode,]) 
            InstallOptionsValues is an array of strings providing
            additional information to InstallOptions for the method to
            install the software. Each entry of this array is related to
            the entry in InstallOptions that is located at the same index
            providing additional information for InstallOptions. \n\nFor
            further information on the use of InstallOptionsValues
            parameter, see the description of the InstallOptionsValues
            parameter of the
            SoftwareInstallationService.InstallFromSoftwareIdentity
            method.
            
        param_image --  The input parameter Image (type [pywbem.Uint8,]) 
            A array of bytes containing the install image.
            
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.InstallFromByteStream.InstallOptions) 
            Options to control the install process. \nSee the
            InstallOptions parameter of the
            SoftwareInstallationService.InstallFromSoftwareIdentity method
            for the description of these values.
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.InstallFromByteStream)
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
        logger.log_debug('Entering %s.cim_method_installfrombytestream()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('job', type='reference', 
        #                   value=pywbem.CIMInstanceName(classname='CIM_ConcreteJob', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.InstallFromByteStream)
        return (rval, out_params)
        
    class Values(object):
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

        class HealthState(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(5)
            Degraded_Warning = pywbem.Uint16(10)
            Minor_failure = pywbem.Uint16(15)
            Major_failure = pywbem.Uint16(20)
            Critical_failure = pywbem.Uint16(25)
            Non_recoverable_error = pywbem.Uint16(30)
            # DMTF_Reserved = ..

        class InstallFromURI(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            URI_not_accessible = pywbem.Uint32(4107)
            # Method_Reserved = 4108..32767
            # Vendor_Specific = 32768..65535
            class InstallOptions(object):
                Defer_target_system_reset = pywbem.Uint16(2)
                Force_installation = pywbem.Uint16(3)
                Install = pywbem.Uint16(4)
                Update = pywbem.Uint16(5)
                Repair = pywbem.Uint16(6)
                Reboot = pywbem.Uint16(7)
                Password = pywbem.Uint16(8)
                Uninstall = pywbem.Uint16(9)
                Log = pywbem.Uint16(10)
                SilentMode = pywbem.Uint16(11)
                AdministrativeMode = pywbem.Uint16(12)
                ScheduleInstallAt = pywbem.Uint16(13)
                # DMTF_Reserved = ..
                # Vendor_Specific = 32768..65535

        class CheckAvailableUpdates(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            Cannot_add_to_Collection = pywbem.Uint32(4108)
            # Method_Reserved = 4109..32767
            # Vendor_Specific = 32768..65535

        class UpdateFromSystemModel(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            Cannot_add_to_Collection = pywbem.Uint32(4108)
            # Method_Reserved = 4109..32767
            # Vendor_Specific = 32768..65535
            class InstallOptions(object):
                Test = pywbem.Uint16(1)

        class CommunicationStatus(object):
            Unknown = pywbem.Uint16(0)
            Not_Available = pywbem.Uint16(1)
            Communication_OK = pywbem.Uint16(2)
            Lost_Communication = pywbem.Uint16(3)
            No_Contact = pywbem.Uint16(4)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

        class SetProxyServerAddress(object):
            OK = pywbem.Uint16(0)
            Failed = pywbem.Uint16(1)

        class DetailedStatus(object):
            Not_Available = pywbem.Uint16(0)
            No_Additional_Information = pywbem.Uint16(1)
            Stressed = pywbem.Uint16(2)
            Predictive_Failure = pywbem.Uint16(3)
            Non_Recoverable_Error = pywbem.Uint16(4)
            Supporting_Entity_in_Error = pywbem.Uint16(5)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

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

        class SetRepositoryAddress(object):
            OK = pywbem.Uint16(0)
            Failed = pywbem.Uint16(1)

        class PrimaryStatus(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(1)
            Degraded = pywbem.Uint16(2)
            Error = pywbem.Uint16(3)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

        class InstallFromSoftwareIdentity(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            Cannot_add_to_Collection = pywbem.Uint32(4108)
            # Method_Reserved = 4109..32767
            # Vendor_Specific = 32768..65535
            class InstallOptions(object):
                Defer_target_system_reset = pywbem.Uint16(2)
                Force_installation = pywbem.Uint16(3)
                Install = pywbem.Uint16(4)
                Update = pywbem.Uint16(5)
                Repair = pywbem.Uint16(6)
                Reboot = pywbem.Uint16(7)
                Password = pywbem.Uint16(8)
                Uninstall = pywbem.Uint16(9)
                Log = pywbem.Uint16(10)
                SilentMode = pywbem.Uint16(11)
                AdministrativeMode = pywbem.Uint16(12)
                ScheduleInstallAt = pywbem.Uint16(13)
                # DMTF_Reserved = ..
                # Vendor_Specific = 32768..65535

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

        class CheckSoftwareIdentity(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Reserved = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            Cannot_add_to_Collection = pywbem.Uint32(4108)
            Asynchronous_Job_already_in_progress = pywbem.Uint32(4109)
            # Method_Reserved = 4110..32767
            # Vendor_Specific = 32768..65535
            class InstallCharacteristics(object):
                Target_automatic_reset = pywbem.Uint16(2)
                System_automatic_reset = pywbem.Uint16(3)
                Separate_target_reset_Required = pywbem.Uint16(4)
                Separate_system_reset_Required = pywbem.Uint16(5)
                Manual_Reboot_Required = pywbem.Uint16(6)
                No_Reboot_Required = pywbem.Uint16(7)
                User_Intervention_recommended = pywbem.Uint16(8)
                MAY_be_added_to_specified_Collection = pywbem.Uint16(9)
                # DMTF_Reserved = ..
                # Vendor_Specific = 0x7FFF..0xFFFF

        class EnabledDefault(object):
            Enabled = pywbem.Uint16(2)
            Disabled = pywbem.Uint16(3)
            Not_Applicable = pywbem.Uint16(5)
            Enabled_but_Offline = pywbem.Uint16(6)
            No_Default = pywbem.Uint16(7)
            Quiesce = pywbem.Uint16(9)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 32768..65535

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

        class SetAutomaticUpdates(object):
            OK = pywbem.Uint16(0)
            Not_Supported = pywbem.Uint16(1)
            Failed = pywbem.Uint16(2)
            class AutomaticUpdates(object):
                No_Automatic_Updates = pywbem.Uint16(0)
                Automatic_Check_for_updates = pywbem.Uint16(1)
                Automatic_Check_and_Download_of_updates = pywbem.Uint16(2)
                Automatic_Check__Download___Install_of_updates = pywbem.Uint16(3)

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

        class StartMode(object):
            Automatic = 'Automatic'
            Manual = 'Manual'

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

        class ChangeAffectedElementsAssignedSequence(object):
            Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Error_Occured = pywbem.Uint32(2)
            Busy = pywbem.Uint32(3)
            Invalid_Reference = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Access_Denied = pywbem.Uint32(6)
            # DMTF_Reserved = 7..32767
            # Vendor_Specified = 32768..65535

        class AutomaticUpdates(object):
            No_Automatic_Updates = pywbem.Uint16(0)
            Automatic_Check_for_updates = pywbem.Uint16(1)
            Automatic_Check_and_Download_of_updates = pywbem.Uint16(2)
            Automatic_Check__Download___Install_of_updates = pywbem.Uint16(3)

        class InstallFromNetworkLocations(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            Cannot_add_to_Collection = pywbem.Uint32(4108)
            # Method_Reserved = 4109..32767
            # Vendor_Specific = 32768..65535
            class InstallOptions(object):
                Update = pywbem.Uint16(1)
                Migrate = pywbem.Uint16(2)
                Update_All = pywbem.Uint16(3)
                Test = pywbem.Uint16(4)

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

        class InstallFromByteStream(object):
            Job_Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Target_In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Job_Started = pywbem.Uint32(4096)
            Unsupported_TargetType = pywbem.Uint32(4097)
            Unattended_silent_installation_not_supported = pywbem.Uint32(4098)
            Downgrade_reinstall_not_supported = pywbem.Uint32(4099)
            Not_enough_memory = pywbem.Uint32(4100)
            Not_enough_swap_space = pywbem.Uint32(4101)
            Unsupported_version_transition = pywbem.Uint32(4102)
            Not_enough_disk_space = pywbem.Uint32(4103)
            Software_and_target_operating_system_mismatch = pywbem.Uint32(4104)
            Missing_dependencies = pywbem.Uint32(4105)
            Not_applicable_to_target = pywbem.Uint32(4106)
            No_supported_path_to_image = pywbem.Uint32(4107)
            # Method_Reserved = 4108..32767
            # Vendor_Specific = 32768..65535
            class InstallOptions(object):
                Defer_target_system_reset = pywbem.Uint16(2)
                Force_installation = pywbem.Uint16(3)
                Install = pywbem.Uint16(4)
                Update = pywbem.Uint16(5)
                Repair = pywbem.Uint16(6)
                Reboot = pywbem.Uint16(7)
                Password = pywbem.Uint16(8)
                Uninstall = pywbem.Uint16(9)
                Log = pywbem.Uint16(10)
                SilentMode = pywbem.Uint16(11)
                AdministrativeMode = pywbem.Uint16(12)
                ScheduleInstallAt = pywbem.Uint16(13)
                # DMTF_Reserved = ..
                # Vendor_Specific = 32768..65535

## end of class RPATH_SoftwareInstallationServiceProvider
    
## get_providers() for associating CIM Class Name to python provider class name
    
def get_providers(env): 
    rpath_softwareinstallationservice_prov = RPATH_SoftwareInstallationService(env)  
    return {'RPATH_SoftwareInstallationService': rpath_softwareinstallationservice_prov} 
