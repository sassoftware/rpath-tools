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


import os

from conary.lib import cfg

class RpathToolsConfiguration(cfg.ConfigFile):
    bootRegistration = (cfg.CfgBool, 0)
    bootUuidFile = (cfg.CfgString, "boot-uuid")
    conaryProxyFilePath = (cfg.CfgString, 
        '/etc/conary/config.d/rpath-tools-conaryProxy')
    contactTimeoutInterval = (cfg.CfgInt, 0)
    debugMode = (cfg.CfgBool, False)
    directMethod = (cfg.CfgList(cfg.CfgString), "")
    disableRegistrationFileName = (cfg.CfgString, 'disableRegistration')
    generatedUuidFile = (cfg.CfgString, "generated-uuid")
    lastPollFileName = (cfg.CfgString, 'lastPoll')
    lastRegistrationFileName= (cfg.CfgString, 'lastRegistration')
    localUuidBackupDirectoryName = (cfg.CfgString, "old-registrations")
    localUuidFile = (cfg.CfgString, "local-uuid")
    logFile = (cfg.CfgString, '/var/log/rpath-tools.log')
    randomWaitFileName = (cfg.CfgString, 'randomWait')
    randomWaitMax = (cfg.CfgInt, 14400)
    registrationInterval = (cfg.CfgInt, 0)
    registrationMethod = (cfg.CfgList(cfg.CfgString), ["DIRECT",])
    registrationPort = (cfg.CfgInt, 13579)
    registrationRetryCount = (cfg.CfgInt, 3)
    remoteCertificateAuthorityStore = (cfg.CfgString, "/etc/conary/rpath-tools/certs")
    requiredNetwork = cfg.CfgString
    retrySlotTime = (cfg.CfgInt, 15)
    sfcbConfigurationFile = (cfg.CfgString, "/etc/conary/sfcb/sfcb.cfg")
    sfcbUrl = (cfg.CfgString, "/tmp/sfcbHttpSocket")
    shutdownDeRegistration = (cfg.CfgBool, 0)
    slpMethod = (cfg.CfgList(cfg.CfgString), ["rpath-inventory",])
    topDir = (cfg.CfgString, "/etc/conary/rpath-tools")
    validateRemoteIdentity = (cfg.CfgBool, True)
    scannerSurveyStore = (cfg.CfgString, "/var/lib/conary-cim/surveys")
    scannerSurveyLockFile = (cfg.CfgString, "/var/lock/subsys/survey")

    def __init__(self, readConfigFiles=False, ignoreErrors=False, root=''):
        cfg.ConfigFile.__init__(self)
        if readConfigFiles:
            self.readFiles()

    def readFiles(self, root=''):
        """
        Populate this configuration object with data from all
        standard locations for rbuild configuration files.
        @param root: if specified, search for config file under the given
        root instead of on the base system.  Useful for testing.
        """
        self.read(root + '/etc/conary/rpath-tools/rpathrc', exception=False)
        if os.environ.has_key("HOME"):
            self.read(root + os.environ["HOME"] + "/" + ".rpathrc",
                      exception=False)
        self.read('rpathrc', exception=False)

    @property
    def bootUuidFilePath(self):
        return os.path.join(self.topDir, self.bootUuidFile)

    @property
    def generatedUuidFilePath(self):
        return os.path.join(self.topDir, self.generatedUuidFile)

    @property
    def localUuidFilePath(self):
        return os.path.join(self.topDir, self.localUuidFile)

    @property
    def localUuidOldDirectoryPath(self):
        return os.path.join(self.topDir, self.localUuidBackupDirectoryName)

    @property
    def lastPollFilePath(self):
        return os.path.join(self.topDir, self.lastPollFileName)

    @property
    def disableRegistrationFilePath(self):
        return os.path.join(self.topDir, self.disableRegistrationFileName)

    @property
    def lastRegistrationFilePath(self):
        return os.path.join(self.topDir, self.lastRegistrationFileName)

    @property
    def randomWaitFilePath(self):
        return os.path.join(self.topDir, self.randomWaitFileName)
