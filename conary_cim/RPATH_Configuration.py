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


"""Python Provider for RPATH_Configuration

Instruments the CIM class RPATH_Configuration

"""

import os
import pywbem

import stub_RPATH_Configuration
import mixin_computersystem
import config_manager
import cim_logger

stubClass = stub_RPATH_Configuration.RPATH_Configuration

class RPATH_Configuration(stubClass, mixin_computersystem.MixInComputerSystem):
    """Instrument the CIM class RPATH_ElementSoftwareIdentity 

    ElementSoftwareIdentity allows a Managed Element to report its software
    related asset information (firmware, drivers, configuration software,
    and etc.)
    
    """

    def _getConfigManager(self, env):
        return config_manager.ConfigManager(env.get_logger())

    def _iterConfigItems(self, env):
        manager = self._getConfigManager(env)
        return manager.iterConfigurations()

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
            manager = self._getConfigManager(env)
            instance = manager.getConfiguration(model.path['SettingID'])
            model.path['CreationClassName'] = model.classname
        model['Value'] = pywbem.CIMProperty('Value', instance.value,
            type='string')

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

        systemCreationClassName, systemName = self.getComputerSystemName(env)

        # Prime model.path with knowledge of the keys, so key values on
        # the CIMInstanceName (model.path) will automatically be set when
        # we set property values on the model. 
        model.path.update(dict(CreationClassName = model.classname,
            SystemName = None, SystemCreationClassName=None,
            SettingID = None))

        for item in self._iterConfigItems(env):
            model.path.update(
                CreationClassName = model.classname,
                SettingID = item.path,
                SystemName = systemName,
                SystemCreationClassName = systemCreationClassName,
            )
            if keys_only:
                yield model
            else:
                yield self.get_instance(env, model)

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
   
            was CreateInstance)
        CIM_ERR_NOT_FOUND (the CIM Instance does not exist -- only valid 
            if modify_existing is True, indicating that the operation
            was ModifyInstance)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.set_instance()'                 % self.__class__.__name__)
        manager = self._getConfigManager(env)
        config = manager.getConfiguration(instance.path['SettingID'])
        config.value = instance['Value']
        return instance


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
        and a list of CIMParameter objects representing th

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
        logger.log_debug('Entering %s.cim_method_applytomse()'                 % self.__class__.__name__)

        manager = self._getConfigManager(env)
        instance = manager.getConfiguration(object_name['SettingID'])
        retval, stdout, stderr = manager.apply(instance)
        # Map return values
        if retval != 0:
            rval = 64
        else:
            rval = 0

        out_params = []
        out_params.append(pywbem.CIMParameter('operationlogs', type='string', 
           value=[str(retval), stdout, stderr]))
        return (pywbem.Uint16(rval), out_params)
        

def get_providers(env):
    prov = RPATH_Configuration(env)
    return {'RPATH_Configuration': prov}

def init(env):
    logName = os.path.basename(__file__)
    logger = cim_logger.Logger(logName, "/var/log/conary-cim.log")
    env.get_logger = lambda _l=logger: _l
