#
# Copyright (c) 2010 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#


import os

from conary.lib import cfg

class rRegisterConfiguration(cfg.ConfigFile):
    bootRegistration = (cfg.CfgBool, 1)
    shutdownDeRegistration = (cfg.CfgBool, 1)
    registrationInterval = (cfg.CfgInt, 1)
    contactTimeoutInterval = (cfg.CfgInt, 3)
    registrationPort = (cfg.CfgInt, 13579)
    registrationMethod = (cfg.CfgList(cfg.CfgString), ["DIRECT",])
    directMethod = (cfg.CfgList(cfg.CfgString), "")
    slpMethod = (cfg.CfgList(cfg.CfgString), ["rpath-inventory",])
    registrationRetryCount = (cfg.CfgInt, 3)
    retrySlotTime = (cfg.CfgInt, 15)
    sfcbUrl = (cfg.CfgString, "/tmp/sfcbHttpSocket")
    topDir = (cfg.CfgString, "/etc/conary/rregister")
    generatedUuidFile = (cfg.CfgString, "generated-uuid")
    localUuidFile = (cfg.CfgString, "local-uuid")
    localUuidBackupDirectoryName = (cfg.CfgString, "old-registrations")
    credentialsDirectoryName = (cfg.CfgString, "credentials")
    credentialsCertFileName = (cfg.CfgString, "credentials.cert")
    credentialsKeyFileName = (cfg.CfgString, "credentials.key")
    sfcbConfigurationFile = (cfg.CfgString, "/etc/conary/sfcb/sfcb.cfg")
    logFile = (cfg.CfgString, '/var/log/rregister')
    lastPollFileName = (cfg.CfgString, 'lastPoll')
    disableRegistrationFileName = (cfg.CfgString, 'disableRegistration')
    lastRegistrationFileName= (cfg.CfgString, 'lastRegistration')
    debugMode = (cfg.CfgBool, False)
    remoteCAFilePath = (cfg.CfgString, "/etc/conary/rregister/remoteCA.cert")
    validateRemoteIdentity = (cfg.CfgBool, True)
    requiredNetwork = cfg.CfgString

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
        self.read(root + '/etc/conary/rpath-tools/registerrc', exception=False)
        if os.environ.has_key("HOME"):
            self.read(root + os.environ["HOME"] + "/" + ".rregisterrc",
                      exception=False)
        self.read('rregisterrc', exception=False)

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
    def credentialsDirectoryPath(self):
        return os.path.join(self.topDir, self.credentialsDirectoryName)

    @property
    def credentialsCertFilePath(self):
        return os.path.join(self.credentialsDirectoryPath,
            self.credentialsCertFileName)

    @property
    def credentialsKeyFilePath(self):
        return os.path.join(self.credentialsDirectoryPath,
            self.credentialsKeyFileName)

    @property
    def lastPollFilePath(self):
        return os.path.join(self.topDir, self.lastPollFileName)

    @property
    def disableRegistrationFilePath(self):
        return os.path.join(self.topDir, self.disableRegistrationFileName)

    @property
    def lastRegistrationFilePath(self):
        return os.path.join(self.topDir, self.lastRegistrationFileName)
