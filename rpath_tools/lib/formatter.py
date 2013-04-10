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


from conary.deps import arch as cny_arch
from conary.deps import deps as cny_deps
from lxml import etree


def getArchFromFlavor(flavor):
    if flavor.members and cny_deps.DEP_CLASS_IS in flavor.members:
        depClass = flavor.members[cny_deps.DEP_CLASS_IS]
        arch = cny_arch.getMajorArch(depClass.getDeps())
        return arch.name
    return ''


class Formatter(object):
    __slots__ = [ 'jobs', 'root', 'changes' ]
    def __init__(self, updateJob):
        self.jobs = []
        if updateJob is not None:
            self.jobs = updateJob.getJobs()
        self.root = None
        self.changes = None

    def format(self):
        self.root = etree.Element('preview')
        self.changes = etree.SubElement(self.root, 'conary_package_changes')
        for oneJob in self.jobs:
            for j in oneJob:
                self._formatJob(j)

    def addObservedVersion(self, troveTup):
        etree.SubElement(self.root, 'observed').text = troveTup.asString(
                withTimestamp=True)

    def addDesiredVersion(self, troveTup):
        etree.SubElement(self.root, 'desired').text = troveTup.asString(
                withTimestamp=True)

    def addUuid(self, uuid):
        etree.SubElement(self.root, 'uuid').text = str(uuid)

    def toxml(self):
        return etree.tostring(self.root)

    def _formatJob(self, job):
        (name, (oldVer, oldFla), (newVer, newFla)) = job[:3]
        if oldVer is None:
            self._formatInstall(name, newVer, newFla)
        elif newVer is None:
            self._formatErase(name, oldVer, oldFla)
        else:
            self._formatUpdate(name, oldVer, oldFla, newVer, newFla)

    def _formatInstall(self, name, version, flavor):
        node = self._newPackageChange('added')
        self._packageSpec(node, 'added_conary_package', name, version, flavor)

    def _formatErase(self, name, version, flavor):
        node = self._newPackageChange('removed')
        self._packageSpec(node, 'removed_conary_package', name, version, flavor)

    def _formatUpdate(self, name, oldVersion, oldFlavor, newVersion, newFlavor):
        node = self._newPackageChange('changed')
        self._packageSpec(node, 'from_conary_package', name, oldVersion, oldFlavor)
        self._packageSpec(node, 'to_conary_package', name, newVersion, newFlavor)

        diff = etree.SubElement(node, 'conary_package_diff')
        oldRev = oldVersion.trailingRevision()
        newRev = newVersion.trailingRevision()
        oldArch = getArchFromFlavor(oldFlavor)
        newArch = getArchFromFlavor(newFlavor)

        self._fieldDiff(diff, 'version',
                oldVersion.freeze(), newVersion.freeze())
        self._fieldDiff(diff, 'revision', oldRev, newRev)
        self._fieldDiff(diff, 'flavor', oldFlavor, newFlavor)
        self._fieldDiff(diff, 'architecture', oldArch, newArch)

    def _newPackageChange(self, type):
        node = etree.SubElement(self.changes, 'conary_package_change')
        etree.SubElement(node, 'type').text = type
        return node

    def _packageSpec(self, parent, tag, name, version, flavor):
        node = etree.SubElement(parent, tag)
        etree.SubElement(node, 'name').text = str(name)
        etree.SubElement(node, 'version').text = version.freeze()
        etree.SubElement(node, 'architecture').text = getArchFromFlavor(flavor)
        etree.SubElement(node, 'flavor').text = str(flavor)
        etree.SubElement(node, 'revision').text = str(
                version.trailingRevision())
        return node

    def _fieldDiff(self, parent, tag, oldValue, newValue):
        if oldValue == newValue:
            return
        node = etree.SubElement(parent, tag)
        etree.SubElement(node, 'from').text = str(oldValue)
        etree.SubElement(node, 'to').text = str(newValue)
