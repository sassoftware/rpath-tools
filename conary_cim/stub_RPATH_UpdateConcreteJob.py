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
from pywbem.cim_provider2 import CIMProvider2

class RPATH_UpdateConcreteJob(CIMProvider2):
    """Instrument the CIM class RPATH_UpdateConcreteJob 

    A concrete version of Job. This class represents a generic and
    instantiable unit of work, such as a batch or a print job.
    
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
        #   model['InstanceID']

        #model['Caption'] = '' # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        #model['DeleteOnCompletion'] = bool() # TODO 
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElapsedTime'] = pywbem.CIMDateTime() # TODO 
        #model['ElementName'] = '' # TODO 
        #model['ErrorCode'] = pywbem.Uint16() # TODO 
        #model['ErrorDescription'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        #model['JobInParameters'] = '' # TODO 
        #model['JobOutParameters'] = '' # TODO 
        #model['JobResults'] = ['',] # TODO 
        #model['JobRunTimes'] = pywbem.Uint32(1) # TODO 
        #model['JobState'] = self.Values.JobState.<VAL> # TODO 
        #model['JobStatus'] = '' # TODO 
        #model['LocalOrUtcTime'] = self.Values.LocalOrUtcTime.<VAL> # TODO 
        #model['MethodName'] = '' # TODO 
        #model['Name'] = '' # TODO (Required)
        #model['Notify'] = '' # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherRecoveryAction'] = '' # TODO 
        #model['Owner'] = '' # TODO 
        #model['PercentComplete'] = pywbem.Uint16() # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['Priority'] = pywbem.Uint32() # TODO 
        #model['RecoveryAction'] = self.Values.RecoveryAction.<VAL> # TODO 
        #model['RunDay'] = pywbem.Sint8() # TODO 
        #model['RunDayOfWeek'] = self.Values.RunDayOfWeek.<VAL> # TODO 
        #model['RunMonth'] = self.Values.RunMonth.<VAL> # TODO 
        #model['RunStartInterval'] = pywbem.CIMDateTime() # TODO 
        #model['ScheduledStartTime'] = pywbem.CIMDateTime() # TODO 
        #model['StartTime'] = pywbem.CIMDateTime() # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        #model['TimeBeforeRemoval'] = pywbem.CIMDateTime() # TODO (Required)
        #model['TimeOfLastStateChange'] = pywbem.CIMDateTime() # TODO 
        #model['TimeSubmitted'] = pywbem.CIMDateTime() # TODO 
        #model['UntilTime'] = pywbem.CIMDateTime() # TODO 
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
        
        while False: # TODO more instances?
            # TODO fetch system resource
            # Key properties    
            #model['InstanceID'] = '' # TODO (type = unicode)
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
        """Implements RPATH_UpdateConcreteJob.RequestStateChange()

        Requests that the state of the job be changed to the value
        specified in the RequestedState parameter. Invoking the
        RequestStateChange method multiple times could result in earlier
        requests being overwritten or lost. \nIf 0 is returned, then the
        task completed successfully. Any other return code indicates an
        error condition.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method RequestStateChange() 
            should be invoked.
        param_requestedstate --  The input parameter RequestedState (type pywbem.Uint16 self.Values.RequestStateChange.RequestedState) 
            RequestStateChange changes the state of a job. The possible
            values are as follows: \nStart (2) changes the state to
            \'Running\'. \nSuspend (3) stops the job temporarily. The
            intention is to subsequently restart the job with \'Start\'.
            It might be possible to enter the \'Service\' state while
            suspended. (This is job-specific.) \nTerminate (4) stops the
            job cleanly, saving data, preserving the state, and shutting
            down all underlying processes in an orderly manner. \nKill (5)
            terminates the job immediately with no requirement to save
            data or preserve the state. \nService (6) puts the job into a
            vendor-specific service state. It might be possible to restart
            the job.
            
        param_timeoutperiod --  The input parameter TimeoutPeriod (type pywbem.CIMDateTime) 
            A timeout period that specifies the maximum amount of time that
            the client expects the transition to the new state to take.
            The interval format must be used to specify the TimeoutPeriod.
            A value of 0 or a null parameter indicates that the client has
            no time requirements for the transition. \nIf this property
            does not contain 0 or null and the implementation does not
            support this parameter, a return code of \'Use Of Timeout
            Parameter Not Supported\' must be returned.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.RequestStateChange)
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
        logger.log_debug('Entering %s.cim_method_requeststatechange()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32 self.Values.RequestStateChange)
        return (rval, out_params)
        
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

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint16 self.Values.ApplyUpdate)
        return (rval, out_params)
        
    def cim_method_geterror(self, env, object_name):
        """Implements RPATH_UpdateConcreteJob.GetError()

        GetError is deprecated because Error should be an array,not a
        scalar.\nWhen the job is executing or has terminated without
        error, then this method returns no CIM_Error instance. However, if
        the job has failed because of some internal problem or because the
        job has been terminated by a client, then a CIM_Error instance is
        returned.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method GetError() 
            should be invoked.

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.GetError)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Error -- (type pywbem.CIMInstance(classname='CIM_Error', ...)) 
            If the OperationalStatus on the Job is not "OK", then this
            method will return a CIM Error instance. Otherwise, when the
            Job is "OK", null is returned.
            

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
        logger.log_debug('Entering %s.cim_method_geterror()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('error', type='string', 
        #                   value=pywbem.CIMInstance(classname='CIM_Error', ...))] # TODO
        #rval = # TODO (type pywbem.Uint32 self.Values.GetError)
        return (rval, out_params)
        
    def cim_method_killjob(self, env, object_name,
                           param_deleteonkill=None):
        """Implements RPATH_UpdateConcreteJob.KillJob()

        KillJob is being deprecated because there is no distinction made
        between an orderly shutdown and an immediate kill.
        CIM_ConcreteJob.RequestStateChange() provides \'Terminate\' and
        \'Kill\' options to allow this distinction. \nA method to kill
        this job and any underlying processes, and to remove any
        \'dangling\' associations.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method KillJob() 
            should be invoked.
        param_deleteonkill --  The input parameter DeleteOnKill (type bool) 
            Indicates whether or not the Job should be automatically
            deleted upon termination. This parameter takes precedence over
            the property, DeleteOnCompletion.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.KillJob)
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
        logger.log_debug('Entering %s.cim_method_killjob()' \
                % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32 self.Values.KillJob)
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

        class HealthState(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(5)
            Degraded_Warning = pywbem.Uint16(10)
            Minor_failure = pywbem.Uint16(15)
            Major_failure = pywbem.Uint16(20)
            Critical_failure = pywbem.Uint16(25)
            Non_recoverable_error = pywbem.Uint16(30)
            # DMTF_Reserved = ..

        class JobState(object):
            New = pywbem.Uint16(2)
            Starting = pywbem.Uint16(3)
            Running = pywbem.Uint16(4)
            Suspended = pywbem.Uint16(5)
            Shutting_Down = pywbem.Uint16(6)
            Completed = pywbem.Uint16(7)
            Terminated = pywbem.Uint16(8)
            Killed = pywbem.Uint16(9)
            Exception = pywbem.Uint16(10)
            Service = pywbem.Uint16(11)
            Query_Pending = pywbem.Uint16(12)
            # DMTF_Reserved = 13..32767
            # Vendor_Reserved = 32768..65535

        class KillJob(object):
            Success = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unknown = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Access_Denied = pywbem.Uint32(6)
            Not_Found = pywbem.Uint32(7)
            # DMTF_Reserved = ..
            # Vendor_Specific = 32768..65535

        class GetError(object):
            Success = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unspecified_Error = pywbem.Uint32(2)
            Timeout = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            Access_Denied = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            # Vendor_Specific = 32768..65535

        class RecoveryAction(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            Do_Not_Continue = pywbem.Uint16(2)
            Continue_With_Next_Job = pywbem.Uint16(3)
            Re_run_Job = pywbem.Uint16(4)
            Run_Recovery_Job = pywbem.Uint16(5)

        class RunDayOfWeek(object):
            _Saturday = pywbem.Sint8(-7)
            _Friday = pywbem.Sint8(-6)
            _Thursday = pywbem.Sint8(-5)
            _Wednesday = pywbem.Sint8(-4)
            _Tuesday = pywbem.Sint8(-3)
            _Monday = pywbem.Sint8(-2)
            _Sunday = pywbem.Sint8(-1)
            ExactDayOfMonth = pywbem.Sint8(0)
            Sunday = pywbem.Sint8(1)
            Monday = pywbem.Sint8(2)
            Tuesday = pywbem.Sint8(3)
            Wednesday = pywbem.Sint8(4)
            Thursday = pywbem.Sint8(5)
            Friday = pywbem.Sint8(6)
            Saturday = pywbem.Sint8(7)

        class ApplyUpdate(object):
            OK = pywbem.Uint16(0)
            Failed = pywbem.Uint16(1)

        class RunMonth(object):
            January = pywbem.Uint8(0)
            February = pywbem.Uint8(1)
            March = pywbem.Uint8(2)
            April = pywbem.Uint8(3)
            May = pywbem.Uint8(4)
            June = pywbem.Uint8(5)
            July = pywbem.Uint8(6)
            August = pywbem.Uint8(7)
            September = pywbem.Uint8(8)
            October = pywbem.Uint8(9)
            November = pywbem.Uint8(10)
            December = pywbem.Uint8(11)

        class CommunicationStatus(object):
            Unknown = pywbem.Uint16(0)
            Not_Available = pywbem.Uint16(1)
            Communication_OK = pywbem.Uint16(2)
            Lost_Communication = pywbem.Uint16(3)
            No_Contact = pywbem.Uint16(4)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

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

        class LocalOrUtcTime(object):
            Local_Time = pywbem.Uint16(1)
            UTC_Time = pywbem.Uint16(2)

        class RequestStateChange(object):
            Completed_with_No_Error = pywbem.Uint32(0)
            Not_Supported = pywbem.Uint32(1)
            Unknown_Unspecified_Error = pywbem.Uint32(2)
            Can_NOT_complete_within_Timeout_Period = pywbem.Uint32(3)
            Failed = pywbem.Uint32(4)
            Invalid_Parameter = pywbem.Uint32(5)
            In_Use = pywbem.Uint32(6)
            # DMTF_Reserved = ..
            Method_Parameters_Checked___Transition_Started = pywbem.Uint32(4096)
            Invalid_State_Transition = pywbem.Uint32(4097)
            Use_of_Timeout_Parameter_Not_Supported = pywbem.Uint32(4098)
            Busy = pywbem.Uint32(4099)
            # Method_Reserved = 4100..32767
            # Vendor_Specific = 32768..65535
            class RequestedState(object):
                Start = pywbem.Uint16(2)
                Suspend = pywbem.Uint16(3)
                Terminate = pywbem.Uint16(4)
                Kill = pywbem.Uint16(5)
                Service = pywbem.Uint16(6)
                # DMTF_Reserved = 7..32767
                # Vendor_Reserved = 32768..65535

        class PrimaryStatus(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(1)
            Degraded = pywbem.Uint16(2)
            Error = pywbem.Uint16(3)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

## end of class RPATH_UpdateConcreteJobProvider
    
## get_providers() for associating CIM Class Name to python provider class name
    
def get_providers(env): 
    rpath_updateconcretejob_prov = RPATH_UpdateConcreteJob(env)  
    return {'RPATH_UpdateConcreteJob': rpath_updateconcretejob_prov} 
