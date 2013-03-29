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


"""Python Provider for RPATH_ElementSoftwareIdentity

Instruments the CIM class RPATH_ElementSoftwareIdentity

"""

import pywbem

from mixin_computersystem import MixInComputerSystem
import stub_RPATH_ElementSoftwareIdentity
import installation_service

try:
    import poll_updater
    POLLUPDATE = True
except ImportError:
    POLLUPDATE = False

stubClass = stub_RPATH_ElementSoftwareIdentity.RPATH_ElementSoftwareIdentity

class RPATH_ElementSoftwareIdentity(stubClass, MixInComputerSystem):
    """Instrument the CIM class RPATH_ElementSoftwareIdentity 

    ElementSoftwareIdentity allows a Managed Element to report its software
    related asset information (firmware, drivers, configuration software,
    and etc.)
    
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

        if POLLUPDATE:
            poll_updater.updatePollFile(logger)

        if withCleanup:
            self._populateTroveCache()

        keyId = model['Antecedent'].keybindings['InstanceID']

        # Fetch the trove from the software map
        (n, v, f), isInstalled = self._conarySoftwareMap[keyId]
        if isInstalled is self.installationService.SystemModelType:
            # From the mof:
            # "Supports"indicates that the software will work with or operate
            # the Managed Element but is or will be installed on a different
            # Managed Element.
            # The system model does exist on the Managed Element, so this may
            # not be correct, but it does make a distinction between the system
            # model and the top-level items, and it is correct on Windows
            model['ElementSoftwareStatus'] = [
                self.Values.ElementSoftwareStatus.Supports,
            ]
        elif isInstalled:
            model['ElementSoftwareStatus'] = [
                self.Values.ElementSoftwareStatus.Current,
                self.Values.ElementSoftwareStatus.Installed,
            ]
        else:
            model['ElementSoftwareStatus'] = [
                self.Values.ElementSoftwareStatus.Available,
            ]
        model['UpgradeCondition'] = self.Values.UpgradeCondition.Owner_Upgradeable
        if withCleanup:
            self._conarySoftwareMap.clear()
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

        if POLLUPDATE:
            poll_updater.updatePollFile(logger)

        # Prime model.path with knowledge of the keys, so key values on
        # the CIMInstanceName (model.path) will automatically be set when
        # we set property values on the model. 
        model.path.update({'Dependent': None, 'Antecedent': None})

        systemCreationClassName, systemName = self.getComputerSystemName(env)

        self._populateTroveCache()
        for troveId in sorted(self._conarySoftwareMap):
            # We need to specify the namespace, otherwise sfcb segfaults.
            model['Dependent'] = pywbem.CIMInstanceName(
                classname=systemCreationClassName,
                keybindings = dict(Name = systemName,
                                   CreationClassName = systemCreationClassName),
                namespace = "root/cimv2")
            model['Antecedent'] = pywbem.CIMInstanceName(
                classname='VAMI_SoftwareIdentity',
                keybindings = dict(
                    InstanceID = troveId),
                namespace = "root/cimv2",
                )
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model, withCleanup=False)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise
        self._conarySoftwareMap.clear()

    def _populateTroveCache(self):
        self._conarySoftwareMap = self.installationService.createTroveMapping()

def get_providers(env):
    rpath_elementsoftwareidentity_prov = RPATH_ElementSoftwareIdentity(env)
    return {
        'VAMI_ElementSoftwareIdentity': rpath_elementsoftwareidentity_prov,
        'RPATH_ElementSoftwareIdentity': rpath_elementsoftwareidentity_prov,
    }
