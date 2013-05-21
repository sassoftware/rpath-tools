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


"""Python Provider for RPATH_SoftwareIdentity

Instruments the CIM class RPATH_SoftwareIdentity

"""

import pywbem

import stub_RPATH_SoftwareIdentity
from rpath_tools.lib import installation_service
import utils

stubClass = stub_RPATH_SoftwareIdentity.RPATH_SoftwareIdentity

class RPATH_SoftwareIdentity(stubClass):
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
        stubClass.__init__(self, env)
        self._conarySoftwareMap = {}
        self.installationService = installation_service.InstallationService()

    def get_instance(self, env, model, withCleanup=True):
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

        if withCleanup:
            self._populateTroveCache()

        troveId = model['InstanceID']

        nvf, isInstalled = self._conarySoftwareMap[troveId]

        modelName = modelDescription = nvf[0]
        if isInstalled is self.installationService.SystemModelType:
            # We use the system model's file mtime as the version timestamp
            verTimestamp = int(nvf[2])
            operatingStatus = self.Values.OperatingStatus.In_Service
            productLabel = self.installationService.SystemModelElementName
            versionString = nvf[1]
        else:
            # Our timestamps are 32-bit, so we store the 2 MSB as buildNumber
            # and the 2LSB as the revision number.
            verTimestamp = int(nvf[1].trailingRevision().getTimestamp())
            operatingStatus = ((isInstalled and
                self.Values.OperatingStatus.In_Service) or
                self.Values.OperatingStatus.Dormant)

            productLabel = str(nvf[1].trailingLabel())
            versionString = "%s[%s]" % (nvf[1].freeze(), str(nvf[2]))

        buildNumber = verTimestamp & 0xFFFF
        revisionNumber = (verTimestamp & 0xFFFF0000) >> 16
        vendorURL = 'http://www.rpath.org/rbuilder'

        model['BuildNumber'] = pywbem.Uint16(buildNumber)
        #model['Caption'] = '' # TODO 
        #model['ClassificationDescriptions'] = ['',] # TODO 
        #model['Classifications'] = [self.Values.Classifications.<VAL>,] # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        model['Description'] = modelDescription
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        model['ElementName'] = modelName
        #model['ExtendedResourceType'] = self.Values.ExtendedResourceType.<VAL> # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        model['HealthState'] = self.Values.HealthState.OK
        # XXX Some of these have hard-coded values
        model['IdentityInfoType'] = ['VMware-VAMI:VendorUUID',
           'VMware-VAMI:ProductRID', 'VMware-VAMI:VendorURL',
           'VMware-VAMI:ProductURL', 'VMware-VAMI:SupportURL',
           'VMware-VAMI:UpdateInfo' ]
        model['IdentityInfoValue'] = ['com.rpath',
            productLabel, vendorURL,
            'http://www.rpath.org/project/remote-update', vendorURL,
            '' ]
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        model['IsEntity'] = True
        model['IsLargeBuildNumber'] = True
        #model['Languages'] = ['',] # TODO 
        model['LargeBuildNumber'] = pywbem.Uint64(verTimestamp)
        model['MajorVersion'] = pywbem.Uint16(0)
        model['Manufacturer'] = 'rPath, Inc.'
        #model['MinExtendedResourceTypeBuildNumber'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeMajorVersion'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeMinorVersion'] = pywbem.Uint16() # TODO 
        #model['MinExtendedResourceTypeRevisionNumber'] = pywbem.Uint16() # TODO 
        model['MinorVersion'] = pywbem.Uint16(0)
        model['Name'] = modelName
        model['OperatingStatus'] = operatingStatus
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherExtendedResourceTypeDescription'] = '' # TODO 
        model['PrimaryStatus'] = self.Values.PrimaryStatus.OK
        model['ReleaseDate'] = pywbem.CIMDateTime(utils.Time.format(verTimestamp))
        model['RevisionNumber'] = pywbem.Uint16(revisionNumber)
        #model['SerialNumber'] = '' # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        #model['TargetOperatingSystems'] = ['',] # TODO 
        model['TargetOSTypes'] = [self.Values.TargetOSTypes.LINUX,]
        #model['TargetTypes'] = ['',] # TODO 
        model['VersionString'] = versionString
        if withCleanup:
            self._conarySoftwareMap.clear()
        return model

    def _populateTroveCache(self):
        self._conarySoftwareMap = self.installationService.createTroveMapping()

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

        self._populateTroveCache()
        for troveId in sorted(self._conarySoftwareMap):
            # Key properties    
            model['InstanceID'] = troveId
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model, withCleanup = False)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise
        self._conarySoftwareMap.clear()

def get_providers(env):
    rpath_softwareidentity_prov = RPATH_SoftwareIdentity(env)
    return {
        'VAMI_SoftwareIdentity': rpath_softwareidentity_prov,
        'RPATH_SoftwareIdentity': rpath_softwareidentity_prov,
    }
