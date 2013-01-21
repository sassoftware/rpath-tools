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


"""Python Provider for RPATH_SoftwareIdentity

Instruments the CIM class RPATH_SoftwareIdentity

"""

import pywbem
from pywbem.cim_provider2 import CIMProvider2

class RPATH_SoftwareIdentity(CIMProvider2):
    """Instrument the CIM class RPATH_SoftwareIdentity 

    SoftwareIdentity provides descriptive information about a software
    component for asset tracking and/or installation dependency
    management. When the IsEntity property has the value TRUE, the
    instance of SoftwareIdentity represents an individually identifiable
    entity similar to Physical Element. SoftwareIdentity does NOT indicate
    whether the software is installed, executing, etc. This extra
    information may be provided through specialized associations to
    Software Identity. For instance, both InstalledSoftwareIdentity and
    ElementSoftwareIdentity may be used to indicate that the software
    identified by this class is installed. SoftwareIdentity is used when
    managing the software components of a ManagedElement that is the
    management focus. Since software may be acquired, SoftwareIdentity can
    be associated with a Product using the ProductSoftwareComponent
    relationship. The Application Model manages the deployment and
    installation of software via the classes, SoftwareFeatures and
    SoftwareElements. SoftwareFeature and SoftwareElement are used when
    the software component is the management focus. The
    deployment/installation concepts are related to the asset/identity
    one. In fact, a SoftwareIdentity may correspond to a Product, or to
    one or more SoftwareFeatures or SoftwareElements - depending on the
    granularity of these classes and the deployment model. The
    correspondence of Software Identity to Product, SoftwareFeature or
    SoftwareElement is indicated using the ConcreteIdentity association.
    Note that there may not be sufficient detail or instrumentation to
    instantiate ConcreteIdentity. And, if the association is instantiated,
    some duplication of information may result. For example, the Vendor
    described in the instances of Product and SoftwareIdentity MAY be the
    same. However, this is not necessarily true, and it is why vendor and
    similar information are duplicated in this class. \nNote that
    ConcreteIdentity can also be used to describe the relationship of the
    software to any LogicalFiles that result from installing it. As above,
    there may not be sufficient detail or instrumentation to instantiate
    this association.
    
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

        #model['BuildNumber'] = pywbem.Uint16() # TODO 
        #model['Caption'] = '' # TODO 
        #model['ClassificationDescriptions'] = ['',] # TODO 
        #model['Classifications'] = [self.Values.Classifications.<VAL>,] # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElementName'] = '' # TODO 
        #model['ExtendedResourceType'] = self.Values.ExtendedResourceType.<VAL> # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['IdentityInfoType'] = ['',] # TODO 
        #model['IdentityInfoValue'] = ['',] # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        #model['IsEntity'] = bool(False) # TODO 
        #model['IsLargeBuildNumber'] = bool(False) # TODO 
        #model['Languages'] = ['',] # TODO 
        #model['LargeBuildNumber'] = pywbem.Uint64() # TODO 
        #model['MajorVersion'] = pywbem.Uint16() # TODO 
        #model['Manufacturer'] = '' # TODO 
        #model['MinExtendedResourceTypeBuildNumber'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeMajorVersion'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeMinorVersion'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeRevisionNumber'] = pywbem.Uint16() # TODO 
        #model['MinorVersion'] = pywbem.Uint16() # TODO 
        #model['Name'] = '' # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherExtendedResourceTypeDescription'] = '' # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['ReleaseDate'] = pywbem.CIMDateTime() # TODO 
        #model['RevisionNumber'] = pywbem.Uint16() # TODO 
        #model['SerialNumber'] = '' # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        #model['TargetOperatingSystems'] = ['',] # TODO 
        #model['TargetOSTypes'] = [self.Values.TargetOSTypes.<VAL>,] # TODO 
        #model['TargetTypes'] = ['',] # TODO 
        #model['VersionString'] = '' # TODO 
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

        class Classifications(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            Driver = pywbem.Uint16(2)
            Configuration_Software = pywbem.Uint16(3)
            Application_Software = pywbem.Uint16(4)
            Instrumentation = pywbem.Uint16(5)
            Firmware_BIOS = pywbem.Uint16(6)
            Diagnostic_Software = pywbem.Uint16(7)
            Operating_System = pywbem.Uint16(8)
            Middleware = pywbem.Uint16(9)
            Firmware = pywbem.Uint16(10)
            BIOS_FCode = pywbem.Uint16(11)
            Support_Service_Pack = pywbem.Uint16(12)
            Software_Bundle = pywbem.Uint16(13)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..0xFFFF

        class TargetOSTypes(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            MACOS = pywbem.Uint16(2)
            ATTUNIX = pywbem.Uint16(3)
            DGUX = pywbem.Uint16(4)
            DECNT = pywbem.Uint16(5)
            Tru64_UNIX = pywbem.Uint16(6)
            OpenVMS = pywbem.Uint16(7)
            HPUX = pywbem.Uint16(8)
            AIX = pywbem.Uint16(9)
            MVS = pywbem.Uint16(10)
            OS400 = pywbem.Uint16(11)
            OS_2 = pywbem.Uint16(12)
            JavaVM = pywbem.Uint16(13)
            MSDOS = pywbem.Uint16(14)
            WIN3x = pywbem.Uint16(15)
            WIN95 = pywbem.Uint16(16)
            WIN98 = pywbem.Uint16(17)
            WINNT = pywbem.Uint16(18)
            WINCE = pywbem.Uint16(19)
            NCR3000 = pywbem.Uint16(20)
            NetWare = pywbem.Uint16(21)
            OSF = pywbem.Uint16(22)
            DC_OS = pywbem.Uint16(23)
            Reliant_UNIX = pywbem.Uint16(24)
            SCO_UnixWare = pywbem.Uint16(25)
            SCO_OpenServer = pywbem.Uint16(26)
            Sequent = pywbem.Uint16(27)
            IRIX = pywbem.Uint16(28)
            Solaris = pywbem.Uint16(29)
            SunOS = pywbem.Uint16(30)
            U6000 = pywbem.Uint16(31)
            ASERIES = pywbem.Uint16(32)
            HP_NonStop_OS = pywbem.Uint16(33)
            HP_NonStop_OSS = pywbem.Uint16(34)
            BS2000 = pywbem.Uint16(35)
            LINUX = pywbem.Uint16(36)
            Lynx = pywbem.Uint16(37)
            XENIX = pywbem.Uint16(38)
            VM = pywbem.Uint16(39)
            Interactive_UNIX = pywbem.Uint16(40)
            BSDUNIX = pywbem.Uint16(41)
            FreeBSD = pywbem.Uint16(42)
            NetBSD = pywbem.Uint16(43)
            GNU_Hurd = pywbem.Uint16(44)
            OS9 = pywbem.Uint16(45)
            MACH_Kernel = pywbem.Uint16(46)
            Inferno = pywbem.Uint16(47)
            QNX = pywbem.Uint16(48)
            EPOC = pywbem.Uint16(49)
            IxWorks = pywbem.Uint16(50)
            VxWorks = pywbem.Uint16(51)
            MiNT = pywbem.Uint16(52)
            BeOS = pywbem.Uint16(53)
            HP_MPE = pywbem.Uint16(54)
            NextStep = pywbem.Uint16(55)
            PalmPilot = pywbem.Uint16(56)
            Rhapsody = pywbem.Uint16(57)
            Windows_2000 = pywbem.Uint16(58)
            Dedicated = pywbem.Uint16(59)
            OS_390 = pywbem.Uint16(60)
            VSE = pywbem.Uint16(61)
            TPF = pywbem.Uint16(62)
            Windows__R__Me = pywbem.Uint16(63)
            Caldera_Open_UNIX = pywbem.Uint16(64)
            OpenBSD = pywbem.Uint16(65)
            Not_Applicable = pywbem.Uint16(66)
            Windows_XP = pywbem.Uint16(67)
            z_OS = pywbem.Uint16(68)
            Microsoft_Windows_Server_2003 = pywbem.Uint16(69)
            Microsoft_Windows_Server_2003_64_Bit = pywbem.Uint16(70)
            Windows_XP_64_Bit = pywbem.Uint16(71)
            Windows_XP_Embedded = pywbem.Uint16(72)
            Windows_Vista = pywbem.Uint16(73)
            Windows_Vista_64_Bit = pywbem.Uint16(74)
            Windows_Embedded_for_Point_of_Service = pywbem.Uint16(75)
            Microsoft_Windows_Server_2008 = pywbem.Uint16(76)
            Microsoft_Windows_Server_2008_64_Bit = pywbem.Uint16(77)
            FreeBSD_64_Bit = pywbem.Uint16(78)
            RedHat_Enterprise_Linux = pywbem.Uint16(79)
            RedHat_Enterprise_Linux_64_Bit = pywbem.Uint16(80)
            Solaris_64_Bit = pywbem.Uint16(81)
            SUSE = pywbem.Uint16(82)
            SUSE_64_Bit = pywbem.Uint16(83)
            SLES = pywbem.Uint16(84)
            SLES_64_Bit = pywbem.Uint16(85)
            Novell_OES = pywbem.Uint16(86)
            Novell_Linux_Desktop = pywbem.Uint16(87)
            Sun_Java_Desktop_System = pywbem.Uint16(88)
            Mandriva = pywbem.Uint16(89)
            Mandriva_64_Bit = pywbem.Uint16(90)
            TurboLinux = pywbem.Uint16(91)
            TurboLinux_64_Bit = pywbem.Uint16(92)
            Ubuntu = pywbem.Uint16(93)
            Ubuntu_64_Bit = pywbem.Uint16(94)
            Debian = pywbem.Uint16(95)
            Debian_64_Bit = pywbem.Uint16(96)
            Linux_2_4_x = pywbem.Uint16(97)
            Linux_2_4_x_64_Bit = pywbem.Uint16(98)
            Linux_2_6_x = pywbem.Uint16(99)
            Linux_2_6_x_64_Bit = pywbem.Uint16(100)
            Linux_64_Bit = pywbem.Uint16(101)
            Other_64_Bit = pywbem.Uint16(102)
            Microsoft_Windows_Server_2008_R2 = pywbem.Uint16(103)
            VMware_ESXi = pywbem.Uint16(104)
            Microsoft_Windows_7 = pywbem.Uint16(105)

        class ExtendedResourceType(object):
            Unknown = pywbem.Uint16(0)
            Other = pywbem.Uint16(1)
            Not_Applicable = pywbem.Uint16(2)
            Linux_RPM = pywbem.Uint16(3)
            HP_UX_Depot = pywbem.Uint16(4)
            Windows_MSI = pywbem.Uint16(5)
            Solaris_Package = pywbem.Uint16(6)
            Macintosh_Disk_Image = pywbem.Uint16(7)
            Debian_linux_Package = pywbem.Uint16(8)
            VMware_vSphere_Installation_Bundle = pywbem.Uint16(9)
            VMware_Software_Bulletin = pywbem.Uint16(10)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

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

        class PrimaryStatus(object):
            Unknown = pywbem.Uint16(0)
            OK = pywbem.Uint16(1)
            Degraded = pywbem.Uint16(2)
            Error = pywbem.Uint16(3)
            # DMTF_Reserved = ..
            # Vendor_Reserved = 0x8000..

## end of class RPATH_SoftwareIdentityProvider
    
## get_providers() for associating CIM Class Name to python provider class name
    
def get_providers(env): 
    rpath_softwareidentity_prov = RPATH_SoftwareIdentity(env)  
    return {'RPATH_SoftwareIdentity': rpath_softwareidentity_prov} 
