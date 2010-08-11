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

class rActivateConfiguration(cfg.ConfigFile):
    CONFIGURATION_FILE_GLOBAL = '/etc/conary/ractivate/ractivaterc'

    bootActivation = (cfg.CfgBool, 1)
    shutdownDeActivation = (cfg.CfgBool, 1)
    activationInterval = (cfg.CfgInt, 1)
    contactTimeoutInterval = (cfg.CfgInt, 3)
    activationPort = (cfg.CfgInt, 13579)
    activationMethod = (cfg.CfgList(cfg.CfgString), ["DIRECT",])
    directMethod = (cfg.CfgList(cfg.CfgString), "")
    slpMethod = (cfg.CfgList(cfg.CfgString), ["rpath-inventory",])
    activationRetryCount = (cfg.CfgInt, 3)
    retrySlotTime = (cfg.CfgInt, 15)
    sfcbUrl = (cfg.CfgString, "/tmp/sfcbHttpSocket")
    topDir = (cfg.CfgString, "/etc/conary/ractivate")
    generatedUuidFile = (cfg.CfgString, "generated-uuid")
    localUuidFile = (cfg.CfgString, "local-uuid")
    localUuidBackupDirectoryName = (cfg.CfgString, "old-registrations")
    credentialsDirectoryName = (cfg.CfgString, "credentials")
    credentialsCertFileName = (cfg.CfgString, "credentials.cert")
    credentialsKeyFileName = (cfg.CfgString, "credentials.key")
    sfcbConfigurationFile = (cfg.CfgString, "/etc/conary/sfcb/sfcb.cfg")
    logFile = (cfg.CfgString, '/var/log/ractivate')
    lastPollFileName = (cfg.CfgString, 'lastPoll')
    disableActivationFileName = (cfg.CfgString, 'disableActivation')
    lastActivationFileName= (cfg.CfgString, 'lastActivation')
    debugMode = (cfg.CfgBool, False)
    remoteCAFilePath = (cfg.CfgString, "/etc/conary/ractivate/remoteCA.cert")
    validateRemoteIdentity = (cfg.CfgBool, True)

    def __init__(self, readConfigFiles=False, ignoreErrors=False, root=''):
        cfg.ConfigFile.__init__(self)
        self.lastConfigFile = None
        if readConfigFiles:
            self.readFiles()

    def readFiles(self, root=''):
        """
        Populate this configuration object with data from all
        standard locations for rbuild configuration files.
        @param root: if specified, search for config file under the given
        root instead of on the base system.  Useful for testing.
        """
        self.read(root + self.CONFIGURATION_FILE_GLOBAL, exception=False)
        if os.environ.has_key("HOME"):
            self.read(root + os.environ["HOME"] + "/" + ".ractivaterc",
                      exception=False)
        self.read('ractivaterc', exception=False)

    def readObject(self, path, f):
        # Record which file we used last, so we know where to write the new
        # config
        ret = cfg.ConfigFile.readObject(self, path, f)
        self.lastConfigFile = path
        return ret

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
    def disableActivationFilePath(self):
        return os.path.join(self.topDir, self.disableActivationFileName)

    @property
    def lastActivationFilePath(self):
        return os.path.join(self.topDir, self.lastActivationFileName)
