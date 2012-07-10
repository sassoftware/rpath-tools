#
# Copyright (c) 2012 rPath, Inc.
#

from conary.deps import deps
from conary import conarycfg, conaryclient, updatecmd, versions

from rpath_tools.client.utils import update_job_formatter

class InstallationServiceError(Exception):
    "Base class"

class NoUpdatesFound(InstallationServiceError):
    "Raised when no updates are available"

class RepositoryError(InstallationServiceError):
    "Raised when a repository error is caught"

class UpdateFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'test' ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, None))

class ConaryClientFactory(object):
    def getClient(self):
        ccfg = conarycfg.ConaryConfiguration(readConfigFiles=True)
        cclient = conaryclient.ConaryClient(ccfg)
        callback = updatecmd.callbacks.UpdateCallback()
        cclient.setUpdateCallback(callback)
        return cclient

class Updater(object):
    conaryClientFactory = ConaryClientFactory

    def __init__(self):
        self.cclient = None

    def _getClient(self, force=False):
        if self.cclient is None or force:
            self.cclient = self.conaryClientFactory().getClient()
        return self.cclient

    conaryClient = property(_getClient)

    def updateOperation(self, sources, flags, callback=None):
        trvSpecList = [ self.parseTroveSpec(x) for x in sources ]
        jobList = [ (x[0], (None, None), (x[1], x[2]), True)
            for x in trvSpecList ]
        cclient = self.conaryClient
        cclient.setUpdateCallback(callback)
        try:
            updateJob = self._newUpdateJob(jobList, flags)
        except NoUpdatesFound:
            fmt = update_job_formatter.Formatter(None)
            fmt.format()
            return fmt
        fmt = update_job_formatter.Formatter(updateJob)
        fmt.format()
        if flags.test:
            return fmt
        self._fixSignals()
        cclient.applyUpdateJob(updateJob, test=flags.test)
        return fmt

    def previewOperation(self, sources):
        flags = UpdateFlags(migrate=True, test=True)
        return self.updateOperation(sources, flags, callback=None)

    @classmethod
    def parseTroveSpec(cls, troveSpec):
        n, v, f = conaryclient.cmdline.parseTroveSpec(troveSpec)
        if f is None:
            f = deps.parseFlavor('')
        v = versions.VersionFromString(v)
        return (n, v, f)

    def _fixSignals(self):
        # TODO: Fix this hack.
        # sfcb broker overrides these signals, but the python library thinks
        # the handlers are None.  This breaks the sigprotect.py conary
        # library.
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)

    def _newUpdateJob(self, applyList, flags):
        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        try:
            cclient.prepareUpdateJob(updateJob, applyList,
                migrate = flags.migrate, test = flags.test)
        except conaryclient.NoNewTrovesError:
            raise NoUpdatesFound
        except conaryclient.errors.RepositoryError, e:
            raise RepositoryError, e, sys.exc_info()[2]
        return updateJob

if __name__ == '__main__':
    import sys
    upd = Updater()
    dom = upd.previewOperation([sys.argv[1]])
    print dom.toxml()
