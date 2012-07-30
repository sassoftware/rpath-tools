from conary import conarycfg
from conary import conaryclient
from conary import updatecmd

from xml.etree import cElementTree as etree

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


class Preview(object):
    conaryClientFactory = ConaryClientFactory

    def __init__(self):
        self.cclient = None

    def _getClient(self, force=False):
        if self.cclient is None or force:
            self.cclient = self.conaryClientFactory().getClient()
        return self.cclient

    conaryClient = property(_getClient)

    @classmethod
    def parseTroveSpec(cls, troveSpec):
        n, v, f = conaryclient.cmdline.parseTroveSpec(troveSpec)
        return (n, v, f)

    def _newUpdateJob(self, applyList, flags):
        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        try:
            suggMap = cclient.prepareUpdateJob(updateJob, applyList,
                migrate = flags.migrate, test = flags.test)
        except conaryclient.NoNewTrovesError:
            raise NoUpdatesFound
        except conaryclient.errors.RepositoryError, e:
            raise RepositoryError, e, sys.exc_info()[2]
        return updateJob

    def _fixSignals(self):
        # TODO: Fix this hack.
        # sfcb broker overrides these signals, but the python library thinks
        # the handlers are None.  This breaks the sigprotect.py conary
        # library.
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)


    def updateOperation(self, sources, flags, callback=None):
        trvSpecList = [ self.parseTroveSpec(x) for x in sources ]
        jobList = [ (x[0], (None, None), (x[1], x[2]), True)
            for x in trvSpecList ]
        cclient = self.conaryClient
        topLevelItems = cclient.getUpdateItemList()
        observed = 'None'
        desired = 'None'
        if topLevelItems:
            topLevelItem = [ (n,v,f) for n,v,f in topLevelItems if
                    n.startswith('group-') and n.endswith('-appliance') ][0]
            if topLevelItem:
                observed = '%s=%s[%s]' % topLevelItem
        if sources:
            desired = sources[0]
        cclient.setUpdateCallback(callback)
        try:
            updateJob = self._newUpdateJob(jobList, flags)
        except NoUpdatesFound:
            updateJob = None
        fmt = update_job_formatter.Formatter(updateJob)
        fmt.format()
        etree.SubElement(fmt.root, 'observed').text = observed
        etree.SubElement(fmt.root, 'desired').text = desired
        if flags.test:
            return fmt.toxml()
        # NEVER RUN THIS NEVER
        # left this in for future
        never = None
        if never:
            self._fixSignals()
            cclient.applyUpdateJob(updateJob, test=flags.test)
            return fmt.toxml()
        return never

    def preview(self, sources):
        flags = UpdateFlags(migrate=True,test=True)
        xml = self.updateOperation(sources, flags)
        if xml:
            return xml
        return '<preview/>'

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    sources = [ 'group-smitty-c6e-goad-appliance=/smitty-c6e-goad.eng.rpath.com@rpath:smitty-c6e-goad-1-devel/1-63-1' ]
    preview = Preview()
    xml = preview.preview(sources)
    print xml
