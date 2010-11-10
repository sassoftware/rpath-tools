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

class RpathToolsConfiguration(cfg.ConfigFile):
    bootRegistration = (cfg.CfgBool, 1)
    conaryProxyFilePath = (cfg.CfgString, 
        '/etc/conary/config.d/rpath-tools-conaryProxy')
    contactTimeoutInterval = (cfg.CfgInt, 3)
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
    registrationInterval = (cfg.CfgInt, 1)
    registrationMethod = (cfg.CfgList(cfg.CfgString), ["DIRECT",])
    registrationPort = (cfg.CfgInt, 13579)
    registrationRetryCount = (cfg.CfgInt, 3)
    remoteCertificateAuthorityStore = (cfg.CfgString, "/etc/conary/rpath-tools/certs")
    requiredNetwork = cfg.CfgString
    retrySlotTime = (cfg.CfgInt, 15)
    sfcbConfigurationFile = (cfg.CfgString, "/etc/conary/sfcb/sfcb.cfg")
    sfcbUrl = (cfg.CfgString, "/tmp/sfcbHttpSocket")
    shutdownDeRegistration = (cfg.CfgBool, 1)
    slpMethod = (cfg.CfgList(cfg.CfgString), ["rpath-inventory",])
    topDir = (cfg.CfgString, "/etc/conary/rpath-tools")
    validateRemoteIdentity = (cfg.CfgBool, True)

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
