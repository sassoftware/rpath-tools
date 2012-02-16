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


import logging
import os
import os.path
import pwd
import sys
import time

from conary.lib import util

from rpath_tools.client import config
from rpath_tools.client import utils

from xml.etree import cElementTree as etree
from rpath_tools.client.sysdisco.scanner import SurveyScanner

from rpath_tools.client.register import LocalUuid
from rpath_tools.client.register import GeneratedUuid

logger = logging.getLogger('client')

def main(cfg=None):
    if not cfg:
        cfg = config.RpathToolsConfiguration()
        cfg.topDir = '/etc/conary'
    r = Scanner(cfg)
    r.scanSystem()
    return r.generatedUuid, r.surveyPath


class Scanner(object):

    def __init__(self, cfg, deviceName=None):
        self.cfg = cfg
        self.surveyScanner = SurveyScanner()
        self.generatedUuid = GeneratedUuid().uuid
        self.localUuidObj = LocalUuid(self.cfg.localUuidFilePath,
                                 self.cfg.localUuidOldDirectoryPath,
                                 deviceName)
        self.targetSystemId = self.localUuidObj.targetSystemId
        self.surveyPath = None

    def setDeviceName(self, deviceName):
        self.localUuidObj.deviceName = deviceName
        self.localUuid = self.localUuidObj.uuid

    @classmethod
    def scanner(self, cfg=None):
        if not cfg:
            cfg = config.RpathToolsConfiguration()
        return Scanner(cfg)


    def writeSurveytoStore(self, xml, store, uuid=None,  uid=None, gid=None):
        """
        Write the Survey to the store, using the supplied uid and gid
        """
        if not uuid:
            uuid = self.generatedUuid
        self.surveyPath = os.path.join(store, 'survey-%s.xml' % uuid )
        if self.surveyPath is None:
            # Already written
            return None
        logger.info("Writing survey as %s" % self.surveyPath)
        util.mkdirChain(os.path.dirname(self.surveyPath))
        f = util.AtomicFile(self.surveyPath, chmod=0600)
        f.write(xml)
        f.commit()
        if uid or gid:
            os.chown(self.surveyPath, uid, gid)
        return self.surveyPath


    def removeSurveyFromStore(self, uuid, store):
        self.surveyPath = os.path.join(store, 'survey-%s.xml' % uuid)
        if self.surveyPath is None:
            return False
        util.removeIfExists(self.surveyPath)
        return True


    @property
    def sfcbConfig(self):
        if self._sfcbCfg is None:
            self._sfcbCfg = self.parseSfcbCfg()
        return self._sfcbCfg


    def parseSfcbCfg(self):
        sfcbFilePath = self.cfg.sfcbConfigurationFile
        try:
            f = file(sfcbFilePath)
        except IOError:
            return {}
        # Get rid of all comments and empty lines
        lines = (x.strip() for x in f)
        lines = (x for x in lines if x and not x.startswith('#'))
        cfgVals = (x.split(':', 1) for x in lines)
        cfgVals = (x for x in cfgVals if len(x) == 2)
        return dict((x.strip(), y.strip()) for (x, y) in cfgVals)


    @classmethod
    def _getUserIds(cls, user):
        try:
            strct = pwd.getpwnam(user)
            return strct.pw_uid, strct.pw_gid
        except KeyError:
            return (0, 0)


    def checkLockFile(self, lockfile):
        if os.path.exists(lockfile):
            return True
        return False


    def createLockFile(self, lockfile, uuid=None):
        if not uuid:
            uuid = self.generatedUuid
        f = open(lockfile, 'w')
        f.write(str(uuid))
        return True


    def removeLockFile(self, lockfile):
        util.removeIfExists(lockfile)
        return True


    def scanSystem(self):
        check = self.checkLockFile(self.cfg.scannerSurveyLockFile)
        if check:
            logger.error(' Survey failed. Lock File Exists: %s' %
                        self.cfg.scannerSurveyLockFile)
            print '  Survey failed. Check the log file at %s' % \
            self.cfg.logFile
            return False
        lock = self.createLockFile(self.cfg.scannerSurveyLockFile)
        start = time.time()
        start_proc = time.clock()
        surveyed = self._scanner()
        if surveyed:
            self.removeLockFile(self.cfg.scannerSurveyLockFile)
            proctime = start_proc - time.clock()
            scantime = start - time.time()
            print '  Survey success. %s' % surveyed
            print '      Scan Time: %s' % scantime
            print '      Process Time: %s' % proctime
            return True
        print '  Survey failed.  Check the log file at %s' % \
            self.cfg.logFile
        return False

    def _scanner(self):
        survey, uuid = self._scan_system()
        if survey is None:
            return survey
        # If the server returned something back, save
        survey_path = self.writeSurveytoStore(survey,
                        self.cfg.scannerSurveyStore, uuid=uuid,
                        uid=None, gid=None)
        return survey_path


    def _scan_system(self):
        logger.info('Attempting to run survey on %s' % self.localUuidObj.uuid)
        print '  Attempting to run survey on %s...' % self.localUuidObj.uuid
        uuid = self.generatedUuid
        dom = self.surveyScanner.toxml()
        etree.SubElement(dom, 'uuid').text = str(uuid)
        xml = etree.tostring(dom)
        return xml, uuid



if __name__ == '__main__':
    sys.exit(main())
