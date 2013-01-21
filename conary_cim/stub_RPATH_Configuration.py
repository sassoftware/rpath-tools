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


"""Python Provider for RPATH_Configuration

Instruments the CIM class RPATH_Configuration

"""

import pywbem
from pywbem.cim_provider2 import CIMProvider2

class RPATH_Configuration(CIMProvider2):
    """Instrument the CIM class RPATH_Configuration 

    RPATH_Configuration class enabling configuration management.
    
    """

    def __init__ (self, env):
        logger = env.get_logger()
        logger.log_debug('Initializing provider %s from %s'                 % (self.__class__.__name__, __file__))

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
        logger.log_debug('Entering %s.get_instance()'                 % self.__class__.__name__)
        

        # TODO fetch system resource matching the following keys:
        #   model['SettingID']
        #   model['SystemName']
        #   model['CreationClassName']
        #   model['SystemCreationClassName']

        #model['Caption'] = '' # TODO 
        #model['Description'] = '' # TODO 
        #model['ElementName'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['InstanceID'] = '' # TODO 
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
        logger.log_debug('Entering %s.enum_instances()'                 % self.__class__.__name__)
                
        # Prime model.path with knowledge of the keys, so key values on
        # the CIMInstanceName (model.path) will automatically be set when
        # we set property values on the model. 
        model.path.update({'CreationClassName': None, 'SettingID': None,
            'SystemName': None, 'SystemCreationClassName': None})
        
        while False: # TODO more instances?
            # TODO fetch system resource
            # Key properties    
            #model['SettingID'] = '' # TODO (type = unicode)    
            #model['SystemName'] = '' # TODO (type = unicode)    
            model['CreationClassName'] = 'RPATH_Configuration'    
            #model['SystemCreationClassName'] = '' # TODO (type = unicode)
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
        logger.log_debug('Entering %s.set_instance()'                 % self.__class__.__name__)
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
        logger.log_debug('Entering %s.delete_instance()'                 % self.__class__.__name__)

        # TODO delete the resource
        raise pywbem.CIMError(pywbem.CIM_ERR_NOT_SUPPORTED) # Remove to implement
        
    def cim_method_verifyoktoapplyincrementalchangetocollection(self, env, object_name,
                                                                param_propertiestoapply=None,
                                                                param_mustbecompletedby=None,
                                                                param_collection=None,
                                                                param_timetoapply=None):
        """Implements RPATH_Configuration.VerifyOKToApplyIncrementalChangeToCollection()

        The VerifyOKToApplyIncrementalChangeToCollection method is used to
        verify that a subset of the properties in this Setting can be
        applied to the referenced Collection of ManagedSystemElements at
        the given time or time interval, without causing adverse effects
        to either the Collection itself or its surrounding environment.
        The net effect is to execute the
        VerifyOKToApplyIncrementalChangeToMSE method against each of the
        Elements that are aggregated by the Collection. This method takes
        four input parameters: Collection (the Collection of
        ManagedSystemElements that is being verified), TimeToApply (which,
        being a datetime, can be either a specific time or a time
        interval), MustBeCompletedBy (which indicates the required
        completion time for the method), and a PropertiesToApply array
        (which contains a list of the property names whose values will be
        verified). If the array is null or empty or contains the string
        "all" as a property name, all Settings properties will be
        verified. If it is set to "none" then no Settings properties will
        be verified. The return value should be 0 if it is okay to apply
        the Setting, 1 if the method is not supported, 2 if the Setting
        cannot be applied within the specified times, and any other number
        if an error occurred. One output parameter, CanNotApply, is
        defined, which is a string array that lists the keys of the
        ManagedSystemElements to which the Setting cannot be applied. This
        parameter enables those Elements to be revisited and either fixed
        or have other corrective action taken on them. \nIn a subclass,
        the set of possible return codes could be specified using a
        ValueMap qualifier on the method. The strings to which the
        ValueMap contents are "translated" can also be specified in the
        subclass as a Values array qualifier.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method VerifyOKToApplyIncrementalChangeToCollection() 
            should be invoked.
        param_propertiestoapply --  The input parameter PropertiesToApply (type [unicode,]) 
            A list of the property names whose values will be verified.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_CollectionOfMSEs', ...)) 
            The Collection of ManagedSystemElements for which the setting
            is being verified.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        CanNotApply -- (type [unicode,]) 
            A string array that lists the keys of the ManagedSystemElements
            to which the Setting cannot be applied.
            

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
        logger.log_debug('Entering %s.cim_method_verifyoktoapplyincrementalchangetocollection()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('cannotapply', type='string', 
        #                   value=['',])] # TODO
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_verifyoktoapplyincrementalchangetomse(self, env, object_name,
                                                         param_propertiestoapply=None,
                                                         param_mse=None,
                                                         param_mustbecompletedby=None,
                                                         param_timetoapply=None):
        """Implements RPATH_Configuration.VerifyOKToApplyIncrementalChangeToMSE()

        The VerifyOKToApplyIncrementalChangeToMSE method is used to verify
        that a subset of the properties in this Setting can be applied to
        the referenced ManagedSystemElement at the given time or time
        interval. This method takes four input parameters: MSE (the
        ManagedSystemElement that is being verified), TimeToApply (which,
        being a datetime, can be either a specific time or a time
        interval), MustBeCompletedBy (which indicates the required
        completion time for the method), and a PropertiesToApply array
        (which contains a list of the property names whose values will be
        verified). If the array is null or empty or contains the string
        "ALL" as a property name, then all Settings properties will be
        verified. If it is set to "NONE", then no Settings properties will
        be verified. The return value should be 0 if it is okay to apply
        the Setting, 1 if the method is not supported, 2 if the Setting
        cannot be applied within the specified times, and any other number
        if an error occurred. In a subclass, the set of possible return
        codes could be specified using a ValueMap qualifier on the method.
        The strings to which the ValueMap contents are "translated" can
        also be specified in the subclass as a Values array qualifier.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method VerifyOKToApplyIncrementalChangeToMSE() 
            should be invoked.
        param_propertiestoapply --  The input parameter PropertiesToApply (type [unicode,]) 
            A list of the property names whose values will be verified.
            
        param_mse --  The input parameter MSE (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedSystemElement', ...)) 
            The ManagedSystemElement for which the Setting is being
            verified.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

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
        logger.log_debug('Entering %s.cim_method_verifyoktoapplyincrementalchangetomse()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_applytocollection(self, env, object_name,
                                     param_continueonerror=None,
                                     param_mustbecompletedby=None,
                                     param_collection=None,
                                     param_timetoapply=None):
        """Implements RPATH_Configuration.ApplyToCollection()

        The ApplyToCollection method performs the application of the
        Setting to the referenced Collection of ManagedSystemElements. The
        net effect is to execute the ApplyToMSE method against each of the
        Elements that are aggregated by the Collection. If the input value
        ContinueOnError is false, this method applies the Setting to all
        Elements in the Collection until it encounters an error. In the
        case of an error, the method stops execution, logs the key of the
        Element that caused the error in the CanNotApply array, and issues
        a return code of 2. If the input value ContinueOnError is true,
        then this method applies the Setting to all of the
        ManagedSystemElements in the Collection, and reports the failed
        Elements in the array, CanNotApply. For the latter, processing
        will continue until the method is applied to all Elements in the
        Collection, regardless of any errors encountered. The key of each
        ManagedSystemElement to which the Setting could not be applied is
        logged into the CanNotApply array. This method takes four input
        parameters: Collection (the Collection of Elements to which the
        Setting is being applied), TimeToApply (which, being a datetime,
        can be either a specific time or a time interval), ContinueOnError
        (true indicates to continue processing when an error is
        encountered), and MustBeCompletedBy (which indicates the required
        completion time for the method). The return value should be 0 if
        the Setting is successfully applied to the referenced Collection,
        1 if the method is not supported, 2 if the Setting was not applied
        within the specified times, 3 if the Setting cannot be applied
        using the input value for ContinueOnError, and any other number if
        an error occurred. One output parameter, CanNotApplystring, is
        defined, which is an array that lists the keys of the
        ManagedSystemElements to which the Setting could not be applied.
        This output parameter has meaning only when the ContinueOnError
        parameter is true. \nIn a subclass, the set of possible return
        codes could be specified using a ValueMap qualifier on the method.
        The strings to which the ValueMap contents are "translated" can
        also be specified in the subclass as a Values array qualifier.
        \nNote: If an error occurs when applying the Setting to a
        ManagedSystemElement in the Collection, the Element must be
        configured as it was when the "Apply" attempt began. That is, the
        Element should not be left in an indeterminate state.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ApplyToCollection() 
            should be invoked.
        param_continueonerror --  The input parameter ContinueOnError (type bool) 
            True means to continue processing when an error is encountered.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_CollectionOfMSEs', ...)) 
            The Collection of ManagedSystemElements to be applied.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        CanNotApply -- (type [unicode,]) 
            A string array that lists the keys of the ManagedSystemElements
            to which the Setting could not be applied.
            

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
        logger.log_debug('Entering %s.cim_method_applytocollection()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('cannotapply', type='string', 
        #                   value=['',])] # TODO
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_verifyoktoapplytocollection(self, env, object_name,
                                               param_mustbecompletedby=None,
                                               param_collection=None,
                                               param_timetoapply=None):
        """Implements RPATH_Configuration.VerifyOKToApplyToCollection()

        The VerifyOKToApplyToCollection method is used to verify that this
        Setting can be applied to the referenced Collection of
        ManagedSystemElements, at the given time or time interval, without
        causing adverse effects to either the Collection itself or its
        surrounding environment. The net effect is to execute the
        VerifyOKToApply method against each of the Elements that are
        aggregated by the Collection. This method takes three input
        parameters: Collection (the Collection of ManagedSystemElements
        that is being verified), TimeToApply (which, being a datetime, can
        be either a specific time or a time interval), and
        MustBeCompletedBy (which indicates the required completion time
        for the method). The return value should be 0 if it is okay to
        apply the Setting, 1 if the method is not supported, 2 if the
        Setting cannot be applied within the specified times, and any
        other number if an error occurred. One output parameter,
        CanNotApply, is defined, which is a string array that lists the
        keys of the ManagedSystemElements to which the Setting cannot be
        applied. This parameter enables those Elements to be revisited and
        either fixed or have other corrective action taken on them. \nIn a
        subclass, the set of possible return codes could be specified,
        using a ValueMap qualifier on the method. The strings to which the
        ValueMap contents are "translated" can also be specified in the
        subclass as a Values array qualifier.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method VerifyOKToApplyToCollection() 
            should be invoked.
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_CollectionOfMSEs', ...)) 
            The Collection of ManagedSystemElements that is being verified.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        CanNotApply -- (type [unicode,]) 
            A string array that lists the keys of the ManagedSystemElements
            to which the Setting cannot be applied.
            

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
        logger.log_debug('Entering %s.cim_method_verifyoktoapplytocollection()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('cannotapply', type='string', 
        #                   value=['',])] # TODO
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_applytomse(self, env, object_name,
                              param_mse=None,
                              param_mustbecompletedby=None,
                              param_timetoapply=None):
        """Implements RPATH_Configuration.ApplyToMSE()

        The ApplyToMSE method performs the actual application of the
        Setting to the referenced ManagedSystemElement. It takes three
        input parameters: MSE (the ManagedSystemElement to which the
        Setting is being applied), TimeToApply (which, being a datetime,
        can be either a specific time or a time interval), and
        MustBeCompletedBy (which indicates the required completion time
        for the method). Note that the semantics of this method are that
        individual Settings are either wholly applied or not applied at
        all to their target ManagedSystemElement. The return value should
        be 0 if the Setting is successfully applied to the referenced
        ManagedSystemElement, 1 if the method is not supported, 2 if the
        Setting was not applied within the specified times, and any other
        number if an error occurred. In a subclass, the set of possible
        return codes could be specified, using a ValueMap qualifier on the
        method. The strings to which the ValueMap contents are
        "translated" can also be specified in the subclass as a Values
        array qualifier. \nNote: If an error occurs when applying the
        Setting to a ManagedSystemElement, the Element must be configured
        as it was when the "Apply" attempt began. That is, the Element
        should not be left in an indeterminate state.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ApplyToMSE() 
            should be invoked.
        param_mse --  The input parameter MSE (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedSystemElement', ...)) 
            The ManagedSystemElement to which the Setting is being applied.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        OperationLogs -- (type [unicode,]) 
            A string array that lists log messages gathered when this
            method was run.
            

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
        logger.log_debug('Entering %s.cim_method_applytomse()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('operationlogs', type='string', 
        #                   value=['',])] # TODO
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_applyincrementalchangetocollection(self, env, object_name,
                                                      param_mustbecompletedby=None,
                                                      param_collection=None,
                                                      param_continueonerror=None,
                                                      param_propertiestoapply=None,
                                                      param_timetoapply=None):
        """Implements RPATH_Configuration.ApplyIncrementalChangeToCollection()

        The ApplyIncrementalChangeToCollection method performs the
        application of a subset of the properties in this Setting to the
        referenced Collection of ManagedSystemElements. The net effect is
        to execute the ApplyIncrementalChangeToMSE method against each of
        the Elements that are aggregated by the Collection. If the input
        value ContinueOnError is false, this method applies the Setting to
        all Elements in the Collection until it encounters an error, in
        which case it stops execution, logs the key of the Element that
        caused the error in the CanNotApply array, and issues a return
        code of 2. If the input value ContinueOnError is true, then this
        method applies the Setting to all of the ManagedSystemElements in
        the Collection, and reports the failed Elements in the array,
        CanNotApply. For the latter, processing will continue until the
        method is applied to all Elements in the Collection, regardless of
        any errors encountered. The key of each ManagedSystemElement to
        which the Setting could not be applied is logged into the
        CanNotApply array. This method takes four input parameters:
        Collection (the Collection of Elements to which the Setting is
        being applied), TimeToApply (which, being a datetime, can be
        either a specific time or a time interval), ContinueOnError (true
        indicates to continue processing when an error is encountered),
        MustBeCompletedBy (which indicates the required completion time
        for the method), and a PropertiesToApply array (which contains a
        list of the property names whose values will be applied). If a
        property is not in this list, it will be ignored by the Apply. If
        the array is null or empty or contains the string "ALL" as a
        property name, then all Settings properties will be applied. If it
        is set to "NONE", then no Settings properties will be applied.
        \nThe return value should be 0 if the Setting is successfully
        applied to the referenced Collection, 1 if the method is not
        supported, 2 if the Setting was not applied within the specified
        time, 3 if the Setting cannot be applied using the input value for
        ContinueOnError, and any other number if an error occurred. One
        output parameter, CanNotApplystring, is defined, which is an array
        that lists the keys of the ManagedSystemElements to which the
        Setting could not be applied. This output parameter has meaning
        only when the ContinueOnError parameter is true. \nIn a subclass,
        the set of possible return codes could be specified using a
        ValueMap qualifier on the method. The strings to which the
        ValueMap contents are "translated" can also be specified in the
        subclass as a Values array qualifier. \nNote: If an error occurs
        when applying the Setting to a ManagedSystemElement in the
        Collection, the Element must be configured as it was when the
        "Apply" attempt began. That is, the Element should not be left in
        an indeterminate state.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ApplyIncrementalChangeToCollection() 
            should be invoked.
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            This parameter indicates the required completion time for the
            method.
            
        param_collection --  The input parameter Collection (type REF (pywbem.CIMInstanceName(classname='CIM_CollectionOfMSEs', ...)) 
            The Collection of Elements to which the Setting is being
            applied.
            
        param_continueonerror --  The input parameter ContinueOnError (type bool) 
            True indicates to continue processing when an error is
            encountered.
            
        param_propertiestoapply --  The input parameter PropertiesToApply (type [unicode,]) 
            A list of the property names whose values will be verified.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            A specific time or a time interval.
            

        Returns a two-tuple containing the return value (type pywbem.Uint32)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        CanNotApply -- (type [unicode,]) 
            A string array that lists the keys of the ManagedSystemElements
            to which the Setting cannot be applied.
            

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
        logger.log_debug('Entering %s.cim_method_applyincrementalchangetocollection()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #out_params+= [pywbem.CIMParameter('cannotapply', type='string', 
        #                   value=['',])] # TODO
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_verifyoktoapplytomse(self, env, object_name,
                                        param_mse=None,
                                        param_mustbecompletedby=None,
                                        param_timetoapply=None):
        """Implements RPATH_Configuration.VerifyOKToApplyToMSE()

        The VerifyOKToApplyToMSE method is used to verify that this Setting
        can be applied to the referenced ManagedSystemElement at the given
        time or time interval. This method takes three input parameters:
        MSE (the Managed SystemElement that is being verified),
        TimeToApply (which, being a datetime, can be either a specific
        time or a time interval), and MustBeCompletedBy (which indicates
        the required completion time for the method). The return value
        should be 0 if it is okay to apply the Setting, 1 if the method is
        not supported, 2 if the Setting cannot be applied within the
        specified times, and any other number if an error occurred. In a
        subclass, the set of possible return codes could be specified
        using a ValueMap qualifier on the method. The strings to which the
        ValueMap contents are "translated" can also be specified in the
        subclass as a Values array qualifier.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method VerifyOKToApplyToMSE() 
            should be invoked.
        param_mse --  The input parameter MSE (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedSystemElement', ...)) 
            The ManagedSystemElement that is being verified.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

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
        logger.log_debug('Entering %s.cim_method_verifyoktoapplytomse()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
    def cim_method_applyincrementalchangetomse(self, env, object_name,
                                               param_propertiestoapply=None,
                                               param_mse=None,
                                               param_mustbecompletedby=None,
                                               param_timetoapply=None):
        """Implements RPATH_Configuration.ApplyIncrementalChangeToMSE()

        The ApplyIncrementalChangeToMSE method performs the actual
        application of a subset of the properties in the Setting to the
        referenced ManagedSystemElement. It takes four input parameters:
        MSE (the ManagedSystem Element to which the Setting is being
        applied), TimeToApply (which, being a datetime, can be either a
        specific time or a time interval), MustBeCompletedBy (which
        indicates the required completion time for the method), and a
        PropertiesToApply array (which contains a list of the property
        names whose values will be applied). If a property is not in this
        list, it will be ignored by the Apply. If the array is null,
        empty, or contains the string "ALL" as a property name, then all
        Settings properties will be applied. If it is set to "NONE", then
        no Settings properties will be applied. \nNote that the semantics
        of this method are that individual Settings are either wholly
        applied or not applied at all to their target
        ManagedSystemElement. The return value should be 0 if the Setting
        is successfully applied to the referenced ManagedSystemElement, 1
        if the method is not supported, 2 if the Setting was not applied
        within the specified times, and any other number if an error
        occurred. In a subclass, the set of possible return codes could be
        specified using a ValueMap qualifier on the method. The strings to
        which the ValueMap contents are "translated" can also be specified
        in the subclass as a Values array qualifier. \nNote: If an error
        occurs when applying the Setting to a ManagedSystemElement, the
        Element must be configured as it was when the "Apply" attempt
        began. That is, the Element should not be left in an indeterminate
        state.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method ApplyIncrementalChangeToMSE() 
            should be invoked.
        param_propertiestoapply --  The input parameter PropertiesToApply (type [unicode,]) 
            A list of the property names whose values will be applied.
            
        param_mse --  The input parameter MSE (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedSystemElement', ...)) 
            The ManagedSystemElement to which the Setting is being applied.
            
        param_mustbecompletedby --  The input parameter MustBeCompletedBy (type pywbem.CIMDateTime) 
            The required completion time for the method.
            
        param_timetoapply --  The input parameter TimeToApply (type pywbem.CIMDateTime) 
            TimeToApply can be either a specific time or a time interval.
            

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
        logger.log_debug('Entering %s.cim_method_applyincrementalchangetomse()'                 % self.__class__.__name__)

        # TODO do something
        raise pywbem.CIMError(pywbem.CIM_ERR_METHOD_NOT_AVAILABLE) # Remove to implemented
        out_params = []
        #rval = # TODO (type pywbem.Uint32)
        return (rval, out_params)
        
## end of class RPATH_ConfigurationProvider
    
## get_providers() for associating CIM Class Name to python provider class name
    
def get_providers(env): 
    rpath_configuration_prov = RPATH_Configuration(env)  
    return {'RPATH_Configuration': rpath_configuration_prov} 
