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

import os
import subprocess
import pywbem
import tempfile
from mixin_computersystem import MixInComputerSystem
import stub_RPATH_SoftwareInstallationService
import RPATH_UpdateConcreteJob

from rpath_tools.lib import jobs

try:
    import poll_updater
    POLLUPDATE = True
except ImportError:
    POLLUPDATE = False

pythonPath = '/usr/conary/bin/python'

class RPATH_SoftwareInstallationService(stub_RPATH_SoftwareInstallationService.RPATH_SoftwareInstallationService, MixInComputerSystem):
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

        model['AutomaticUpdates'] = self.Values.AutomaticUpdates.No_Automatic_Updates
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
        model['RepositoryAddress'] = 'foobar'
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
            model['CreationClassName'] = 'VAMI_SoftwareInstallationService'
            model['Name'] = 'rPath Software Installation Service'
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

        if POLLUPDATE:
            poll_updater.updatePollFile(logger)

        if param_source and param_source.has_key('InstanceID'):
            instanceId = param_source['InstanceID']
        else:
            instanceId = None

        # Create update job
        task = jobs.UpdateAllTask().new()
        task(instanceId)

        # XXX Should be VAMI_UpdateConcreteJob
        job = pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob',
            keybindings = dict(
                InstanceID = RPATH_UpdateConcreteJob.RPATH_UpdateConcreteJob.createInstanceID(task.get_job_id())),
            namespace = "root/cimv2")

        out_params = []
        out_params.append(pywbem.CIMParameter('job', type='reference',
                      value=job))
        rval = self.Values.InstallFromSoftwareIdentity.Method_Parameters_Checked___Job_Started
        return (rval, out_params)

    def cim_method_installfromnetworklocations(self, env, object_name,
                                               param_managementnodeaddresses=None,
                                               param_sources=None,
                                               param_installoptions=None,
                                               param_target=None,
                                               param_installoptionvalues=None):
        """Implements RPATH_SoftwareInstallationService.InstallFromNetworkLocations()

        Start a job to update or migrate software on a ManagedElement
        (Target).
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method InstallFromNetworkLocations() 
            should be invoked.
        param_sources --  The input parameter Sources (type [unicode,]) 
            References to the locations
            
        param_installoptions --  The input parameter InstallOptions (type [pywbem.Uint16,] self.Values.InstallFromNetworkLocations.InstallOptions) 
            blah
            
        param_target --  The input parameter Target (type REF (pywbem.CIMInstanceName(classname='CIM_ManagedElement', ...)) 
            The installation target.
            
        param_installoptionvalues --  The input parameter InstallOptionValues (type [unicode,]) 
            blah
            

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

        if POLLUPDATE:
            poll_updater.updatePollFile(logger)

        out_params = []

        if param_managementnodeaddresses:
            try:
                import helper_rpath_tools
                registration = helper_rpath_tools.Registration()
                registration.setConaryProxy(param_managementnodeaddresses)
            except Exception:
                pass

        # Filter out empty params, only needed to bypass a problem in yawn
        # dropping the trailing ]
        param_sources = [ x for x in (param_sources or []) if x ]
        if not param_sources:
            # XXX if no sources specified, result should be an error of some
            # sort
            rval = self.Values.InstallFromNetworkLocations.Job_Completed_with_No_Error
            return (rval, out_params)

        # Extract flags
        optionsMap = {
            self.Values.InstallFromNetworkLocations.InstallOptions.Update :
                "-mupdate",
            self.Values.InstallFromNetworkLocations.InstallOptions.Migrate :
                "-mmigrate",
            self.Values.InstallFromNetworkLocations.InstallOptions.Update_All :
                "-mupdateall",
            self.Values.InstallFromNetworkLocations.InstallOptions.Test :
                "-t",
        }

        args = [optionsMap[x] for x in param_installoptions if x in optionsMap]
        execPath = os.path.join(os.path.dirname(jobs.__file__), 'jobs.py')
        args.insert(0, execPath)
        args.insert(0, pythonPath)
        for source in param_sources:
            args.append("-p%s" % source)

        # Use subprocess to start the update job.  jobs.py double forks,
        # so the wait will return almost immediately.
        concreteJobProc = subprocess.Popen(args, stdout=subprocess.PIPE)
        concreteJobProc.wait()
        # job id is printed to standard out
        stdoutdata, stderrdata = concreteJobProc.communicate()
        concreteJobId = stdoutdata.strip('\n')

        # XXX Should be VAMI_UpdateConcreteJob
        job = pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob',
            keybindings = dict(
                InstanceID = RPATH_UpdateConcreteJob.RPATH_UpdateConcreteJob.createInstanceID(concreteJobId)),
                namespace = "root/cimv2")

        out_params = []
        out_params.append(pywbem.CIMParameter('job', type='reference',
                      value=job))
        rval = self.Values.InstallFromNetworkLocations.Method_Parameters_Checked___Job_Started
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

        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(param_systemmodel)
        tmpf.flush()
        tmpf.close()

        execPath = os.path.join(os.path.dirname(jobs.__file__), 'jobs.py')
        args = [ pythonPath, execPath, '--system-model-path', tmpf.name, '--mode', 'sync' ]

        # Use subprocess to start the update job.  jobs.py double forks,
        # so the wait will return almost immediately.
        concreteJobProc = subprocess.Popen(args, stdout=subprocess.PIPE)
        concreteJobProc.wait()
        # job id is printed to standard out
        stdoutdata, stderrdata = concreteJobProc.communicate()
        concreteJobId = stdoutdata.strip('\n')

        # The concrete job should have picked up the file by now, get
        # rid of it
        os.unlink(tmpf.name)

        job = pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob',
            keybindings = dict(
                InstanceID = RPATH_UpdateConcreteJob.RPATH_UpdateConcreteJob.createInstanceID(concreteJobId)),
                namespace = "root/cimv2")

        out_params = []
        out_params.append(pywbem.CIMParameter('job', type='reference',
                      value=job))
        rval = self.Values.UpdateFromSystemModel.Method_Parameters_Checked___Job_Started
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

        if POLLUPDATE:
            poll_updater.updatePollFile(logger)

        # Create update job
        task = jobs.UpdateCheckTask().new()
        task()

        # XXX Should be VAMI_UpdateConcreteJob
        job = pywbem.CIMInstanceName(classname='RPATH_UpdateConcreteJob',
            keybindings = dict(
                InstanceID = RPATH_UpdateConcreteJob.RPATH_UpdateConcreteJob.createInstanceID(task.get_job_id())),
            namespace = "root/cimv2")

        out_params = []
        out_params.append(pywbem.CIMParameter('job', type='reference',
                      value=job))
        rval = self.Values.CheckAvailableUpdates.Method_Parameters_Checked___Job_Started
        return (rval, out_params)

def get_providers(env):
    rpath_softwareinstallationservice_prov = RPATH_SoftwareInstallationService(env)  
    return {
        'VAMI_SoftwareInstallationService': rpath_softwareinstallationservice_prov,
        'RPATH_SoftwareInstallationService': rpath_softwareinstallationservice_prov,
    }
