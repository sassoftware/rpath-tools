#
# Copyright (c) rPath, Inc.
#

from conary import trovetup
from collections import namedtuple
from xml.etree import cElementTree as etree

import rpm

from conary.deps import deps
from conary import rpmhelper
from conary import conarycfg
from conary import conaryclient
from conary.lib import util
from conary.lib.sha1helper import sha256ToString

class IDFactory(object):
    def __init__(self):
        self._cur = 0
        self._refs = {}

    def getId(self, obj):
        if id(obj) not in self._refs:
            self._refs[id(obj)] = self._cur
            self._cur += 1

        return str(self._refs[id(obj)])


class NEVRA(namedtuple('nevra', 'name epoch version release arch')):
    __slots__ = ()


class RPMInfo(namedtuple('RPMInfo', 'nevra description installtime size '
    'sha1header license')):
    def __new__(cls, name, epoch, version, release, arch, description,
        installtime, size, sha1header, license):

        nevra = NEVRA(name, epoch, version, release, arch)
        return tuple.__new__(cls, (nevra, description, installtime, size,
            sha1header, license))

    @classmethod
    def fromHeader(cls, hdr):
        name = hdr[rpmhelper.NAME]
        epoch = hdr[rpmhelper.EPOCH]
        version = hdr[rpmhelper.VERSION]
        release = hdr[rpmhelper.RELEASE]
        arch = hdr[rpmhelper.ARCH]

        desc = hdr[rpmhelper.DESCRIPTION]
        installtime = hdr[1008]
        size = hdr[1009]
        sha1 = hdr[rpmhelper.SIG_SHA1]
        license = hdr[1014]

        return cls(name, epoch, version, release, arch, desc, installtime,
            size, sha1, license)

    def toxml(self, id):
        root = etree.Element('rpm_package', dict(id=id))
        rpm_package_info = etree.SubElement(root, 'rpm_package_info')
        name = etree.SubElement(rpm_package_info, 'name')
        name.text = self.nevra.name
        epoch = etree.SubElement(rpm_package_info, 'epoch')
        if self.nevra.epoch is not None:
            epoch.text = str(self.nevra.epoch)
        version = etree.SubElement(rpm_package_info, 'version')
        version.text = self.nevra.version
        release = etree.SubElement(rpm_package_info, 'release')
        release.text = self.nevra.release
        arch = etree.SubElement(rpm_package_info, 'architecture')
        arch.text = self.nevra.arch
        description = etree.SubElement(rpm_package_info, 'description')
        if self.description:
            description.text = self.description.decode('utf8', 'replace')
        sig = etree.SubElement(rpm_package_info, 'signature')
        sig.text = self.sha1header

        install_date = etree.SubElement(root, 'install_date')
        install_date.text = str(self.installtime)

        license = etree.SubElement(root, 'license')
        if self.license:
            license.text = self.license

        return root

    def toXmlInfo(self, id):
        root = etree.Element('rpm_package_info', dict(id=id))
        name = etree.SubElement(root, 'name')
        name.text = self.nevra.name
        epoch = etree.SubElement(root, 'epoch')
        if self.nevra.epoch is not None:
            epoch.text = str(self.nevra.epoch)
        version = etree.SubElement(root, 'version')
        version.text = self.nevra.version
        release = etree.SubElement(root, 'release')
        release.text = self.nevra.release
        arch = etree.SubElement(root, 'architecture')
        arch.text = self.nevra.arch
        description = etree.SubElement(root, 'description')
        if self.description:
            description.text = self.description.decode('utf8', 'replace')

        sig = etree.SubElement(root, 'signature')
        sig.text = self.sha1header

        license = etree.SubElement(root, 'license')
        if self.license:
            license.text = self.license

        return root


class MSIInfo(namedtuple('msiInfo', 'name version productCode')):
    __slots__ = ()


class ConaryInfo(namedtuple('ConaryInfo', 'nvf description revision '
        'architecture signature nevra msi license installtime isTopLevel')):
    __slots__ = ()

    def toxml(self, id):
        root = etree.Element('conary_package', dict(id=id))
        conary_package_info = etree.SubElement(root, 'conary_package_info')
        name = etree.SubElement(conary_package_info, 'name')
        name.text = self.nvf.name
        version = etree.SubElement(conary_package_info, 'version')
        version.text = self.nvf.version.freeze()
        flavor = etree.SubElement(conary_package_info, 'flavor')
        flavor.text = str(self.nvf.flavor)
        if self.isTopLevel:
            etree.SubElement(conary_package_info, 'is_top_level').text = 'true'
        description = etree.SubElement(conary_package_info, 'description')
        if self.description:
            description.text = self.description.decode('utf8', 'replace')
        revision = etree.SubElement(conary_package_info, 'revision')
        revision.text = self.revision
        architecture = etree.SubElement(conary_package_info, 'architecture')
        architecture.text = self.architecture
        signature = etree.SubElement(conary_package_info, 'signature')
        if self.signature is not None:
            signature.text = self.signature

        install_date = etree.SubElement(root, 'install_date')
        if self.installtime:
            install_date.text = str(self.installtime)

        # TODO not implemented in conary yet
        license = etree.SubElement(root, 'license')
        if self.license:
            license.text = self.license

        return root


class SystemModel(conaryclient.systemmodel.SystemModelFile):
    def __init__(self, sysmodel):
        super(SystemModel, self).__init__(
            sysmodel.model, sysmodel.fileName)

    def toxml(self):
        root = etree.Element('system_model')
        etree.SubElement(root, 'contents').text = self.contents
        etree.SubElement(root, 'modified_date').text = str(int(self.mtime))
        return root


class AbstractPackageScanner(object):
    def __init__(self):
        self._results = None
        self._client = None

    def scan(self):
        raise NotImplementedError

    def tomodel(self):
        raise NotImplementedError


class RPMScanner(AbstractPackageScanner):
    def scan(self):
        if self._results:
            return self._results

        ts = rpm.TransactionSet()

        mi = ts.dbMatch()

        hdrs = [ RPMInfo.fromHeader(x) for x in mi ]
        self._results = dict((x.nevra, x) for x in hdrs)

        return self._results


class ConaryScanner(AbstractPackageScanner):
    @property
    def client(self):
        if self._client is None:
            cfg = conarycfg.ConaryConfiguration(True)
            self._client = conaryclient.ConaryClient(cfg)
        return self._client

    def _getDb(self):
        db = self.client.getDatabase()
        return db

    def getSystemModel(self):
        sysmodel = self.client.getSystemModel()
        if sysmodel is None:
            return None
        return SystemModel(sysmodel)

    def scan(self):
        if self._results:
            return self._results

        db = self._getDb()

        ISDepClass = deps.InstructionSetDependency

        topLevelItems = set(self.client.getUpdateItemList())

        self._results = {}
        # We cannot use the iterator here, it keeps the database locked, and
        # fetching the trove fails later
        allTroves = list(db.iterAllTroves())
        for nvf in allTroves:
            if not isinstance(nvf, trovetup.TroveTuple):
                # Older versions of Conary did not return a trove tuple
                nvf = trovetup.TroveTuple(*nvf)

            trv = db.getTrove(nvf.name, nvf.version, nvf.flavor)

            revision = nvf.version.trailingRevision().asString()

            arch = ' '.join(str(x) for x in nvf.flavor.iterDepsByClass(ISDepClass))

            sig = None
            digest = trv.troveInfo.sigs.vSigs.getDigest(1)
            if digest:
                sig = sha256ToString(digest)

            nevra = None
            rpm = trv.troveInfo.capsule.rpm
            if rpm.name():
                nevra = NEVRA(rpm.name(), rpm.epoch(), rpm.version(),
                    rpm.release(), rpm.arch())

            msiInfo = None
            msi = trv.troveInfo.capsule.msi
            if msi.name():
                msiInfo = MSIInfo(msi.name(), msi.version(), msi.productCode())

            description = trv.troveInfo.metadata.get().get('longDesc')
            license = trv.troveInfo.metadata.get().get('licenses')
            if hasattr(trv.troveInfo, 'installTime'):
                installTime = trv.troveInfo.installTime()
            else:
                installTime = None

            isTopLevel = None
            if nvf in topLevelItems:
                isTopLevel = True
            cinfo = ConaryInfo(nvf, description, revision,
                    arch, sig, nevra, msiInfo, license, installTime,
                    isTopLevel)

            self._results[cinfo.nvf] = cinfo

        return self._results


class WindowsScanner(AbstractPackageScanner):
    pass


class PackageScanner(object):
    def __init__(self, idFactory):
        self._idfactory = idFactory
        self._rpmScanner = RPMScanner()
        self._conaryScanner = ConaryScanner()
        self._windowsScanner = WindowsScanner()

    def scan(self):
        rpmData = self._rpmScanner.scan()
        conaryData = self._conaryScanner.scan()
        return rpmData, conaryData

    def getSystemModel(self):
        return self._conaryScanner.getSystemModel()

    def toxml(self):
        rpms, troves = self.scan()

        nevraMap = {}
        conary_packages = etree.Element('conary_packages')
        for pkg in troves.itervalues():
            nodeId = self._idfactory.getId(pkg)
            node = pkg.toxml(nodeId)
            rpminfo = rpms.get(pkg.nevra) if pkg.nevra else None
            if rpminfo:
                rpmId = self._idfactory.getId(rpminfo)
                child = node.find('.//conary_package_info')
                child.append(rpminfo.toXmlInfo(rpmId))
                nevraMap[pkg.nevra] = nodeId 
            conary_packages.append(node)

        rpm_packages = etree.Element('rpm_packages')
        for pkg in rpms.itervalues():
            node = pkg.toxml(self._idfactory.getId(pkg))
            if pkg.nevra in nevraMap:
                cnyId = nevraMap.get(pkg.nevra)
                etree.SubElement(node, 'conary_package', dict(id=cnyId))
                etree.SubElement(node, 'encapsulated').text = 'true'
            else:
                etree.SubElement(node, 'encapsulated').text = 'false'
            rpm_packages.append(node)

        return rpm_packages, conary_packages

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

    scanner = PackageScanner(IDFactory())

    root = etree.Element('survey')
    for result in scanner.toxml():
        root.append(result)

    xml = etree.tostring(root)

    print xml
    print >>sys.stderr, 'conary packages:', len(scanner._conaryScanner._results)
    print >>sys.stderr, 'rpm packages:', len(scanner._rpmScanner._results)

    from lxml import etree
    et = etree.fromstring(xml)
    print etree.tostring(et, pretty_print=True)
