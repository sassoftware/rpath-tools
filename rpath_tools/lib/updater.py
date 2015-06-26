#!/usr/conary/bin/python2.6
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


from conary.lib import util
from conary import trovetup

from rpath_tools.lib import update
from rpath_tools.lib import jobs
from rpath_tools.lib import errors
from rpath_tools.lib import installation_service

import tempfile
import time
import os

import logging

logger = logging.getLogger(__name__)


class Updater(update.UpdateService):

    def __init__(self, value=None):
        super(Updater, self).__init__()
        self.tmpDir = self.conaryCfg.tmpDir

    def storeTempSystemModel(self, data):
        fd, path = tempfile.mkstemp(prefix='system-model.', dir=self.tmpDir)
        try:
            f = os.fdopen(fd, 'w')
            f.write(str(str(data)))
        except Exception, e:
            #FIXME
            raise Exception, str(e)
        return path

    def updateOperation(self, sources=None, systemModel=None,
                            preview=True, update=False):
        '''
        system-model sources must be a string representation of
        the system-model file
        classic method sources is a list of top level items

        '''
        if self.isSystemModel:
            if not systemModel:
                systemModel = file(self.systemModelPath).read()
            tempSystemModelPath = self.storeTempSystemModel(systemModel)
            if update:
                task = jobs.UpdatePreviewTask().new()
            else:
                task = jobs.SyncPreviewTask().new()

            # Currently we have to call the steps manually
            # to avoid a double fork
            task.preFork(tempSystemModelPath)
            task.run(tempSystemModelPath)
            if not preview:
                return task.job.keyId
        else:
            # WARNING if preview is set to False the update will be applied
            flags = installation_service.InstallationService.UpdateFlags(
                                migrate=True, test=preview)
            task = jobs.startUpdateOperation(sources=sources, flags=flags)
            finalStates = set(['Completed', 'Exception'])
            while task.job.state not in finalStates:
                time.sleep(1)
            if task.job.state != 'Completed':
                raise Exception(task.job.content)
        xml = task.job.content
        return xml

    def applyOperation(self, jobid):
        xml = '<preview/>'
        if self.isSystemModel:
            task = jobs.SyncApplyTask().load(jobid)
            # Currently we have to call the steps manually
            # to avoid a double fork
            task.preFork()
            task.run()
            xml = task.job.content
        else:
            logger.error('Classic systems do not'
                ' freeze jobs so we can not apply a frozen job')
            raise errors.NotImplementedError
        return xml

    def downloadOperation(self, jobid):
        if self.isSystemModel:
            task = jobs.DownloadTask().load(jobid)
            # Currently we have to call the steps manually
            # to avoid a double fork
            task.preFork()
            task.run()
            xml = task.job.content
        else:
            logger.error('Classic systems do not'
                ' freeze jobs so we can not apply a frozen job')
            raise errors.NotImplementedError
        return xml

    def preview(self, sources=None, systemModel=None):
        # Stub for preview operation
        preview_xml = self.updateOperation(sources, systemModel)

        # jobid for apply will be in preview
        return preview_xml

    def apply(self, jobid):
        # Stub for apply operation
        apply_xml = self.applyOperation(jobid)
        return apply_xml

    def getTopLevelItemsAllVersions(self):
        topLevelItems = sorted(self.conaryClient.getUpdateItemList())
        allversions = {}
        tops = [ trovetup.TroveTuple(name, version, flavor) for
                            name, version, flavor in topLevelItems ]

        for top in tops:
            label = top.version.trailingLabel()
            query = { top.name : { label : None } }
            allversions.update(
                        self.conaryClient.repos.getTroveVersionsByLabel(query))

        for name, versions in allversions.items():
            trovespeclist = []
            for version, flavors in versions.items():
                flavor = None
                if self.conaryCfg.flavorPreferences:
                    flavor = [ x for x in flavors
                        if x.satisfies(self.conaryCfg.flavorPreferences[0]) ]
                if isinstance(flavor, list) and len(flavor):
                    trovespeclist.append(trovetup.TroveSpec(
                            name, version.asString()[1:], str(flavor[0])))

        return trovespeclist

    def convertToPartialSystemModel(self, sources, commands):
        op = 'update'
        if 'install' in commands:
            op = 'install'
        pkglist = [ trovetup.TroveSpec(x) for x in sources ]
        possible = self.getTopLevelItemsAllVersions()
        contents = []
        if pkglist:
            for pkg in pkglist:
                if pkg not in possible:
                    logger.warn("%s is not in current search path or it is a new pkg" % str(pkg))
                update = ' '.join([op, pkg.asString() + '\n'])
                contents.append(update)
        newsysmodel = ''.join(contents)
        systemModelPath = '/tmp/partial-system-model.debug'
        file(systemModelPath, "w").write(newsysmodel)
        return newsysmodel

    def jsonify(self, xml):
        import json
        from lxml import etree

        root = etree.fromstring(xml)

        def _handler(root):
            result = dict()
            if hasattr(root, 'attrib'):
                result.update(root.attrib)
            for e in root:
                if len(e):
                    if hasattr(e, 'attrib'):
                        result.update(e.attrib)
                    obj = _handler(e)
                else:
                    obj = e.text
                if result.get(e.tag):
                    if hasattr(result[e.tag], "append"):
                        result[e.tag].append(obj)
                    else:
                        result[e.tag] = [result[e.tag], obj]
                else:
                    result[e.tag] = obj
            return result
        dump = {root.tag: _handler(root)}
        return json.dumps(dump)

    def cmdlineUpdate(self, sources, commands=None,
                            xml=False, json=False):
        if json:
            xml = True

        if self.isSystemModel:
            partialSystemModel = self.convertToPartialSystemModel(sources, commands)
            results = self.updateOperation(systemModel=partialSystemModel,
                                           preview=xml, update=True)
        else:
            results = self.updateOperation(sources, preview=xml, update=True)
        if json:
            results = self.jsonify(results)
        return results

    def cmdlineDownload(self, jobid, xml=False, json=False):
        results = self.downloadOperation(jobid)
        if json:
            return self.jsonify(results)
        if xml:
            return results
        return

    def cmdlineApply(self, jobid, xml=False, json=False):
        results = self.applyOperation(jobid)
        if json:
            return self.jsonify(results)
        if xml:
            return results
        return

    def debug(self, sources, commands=None, xml=False, json=False):
        pass


if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    fileName = sys.argv[1]
    try:
        with open(fileName) as f:
            blob=f.read()
    except EnvironmentError:
        print 'oops'

