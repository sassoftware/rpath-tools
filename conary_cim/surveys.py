#!/usr/bin/python2.6
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

from rpath_tools.lib import stored_objects

class Survey(stored_objects.FlatStoredObject):
    prefix = "surveys"

    @property
    def id(self):
        return self._idFromFilename(self.keyId)

    @classmethod
    def _stripPrefix(cls, s, prefix):
        if not s.startswith(prefix):
            return s
        return s[len(prefix):]

    @classmethod
    def _stripSuffix(cls, s, suffix):
        if not s.endswith(suffix):
            return s
        return s[:-len(suffix)]

    @classmethod
    def _idFromFilename(cls, filename):
        return cls._stripSuffix(cls._stripPrefix(filename, 'survey-'), '.xml')

    @classmethod
    def _filenameFromId(cls, identifier):
        return "survey-%s.xml" % identifier

class SurveyFactory(stored_objects.StoredObjectsFactory):
    factory = Survey

class SurveyService(object):
    storagePath = "/var/lib/conary-cim"
    SurveyFactoryClass = SurveyFactory

    def __init__(self):
        self._sfact = None

    @property
    def surveyFactory(self):
        if self._sfact is None:
            self._sfact = self.SurveyFactoryClass(self.storagePath)
        return self._sfact

    def list(self):
        for s in self.surveyFactory:
            yield s

    def scan(self, job, desiredTopLevelItems):
        from rpath_tools.client import config
        from rpath_tools.client.scan import Scanner

        cfg = config.RpathToolsConfiguration()
        cfg.topDir = '/etc/conary'

        r = Scanner(cfg)

        r.scanSystemCIM(desiredTopLevelItems)

        job.content = str(r.surveyUuid)

    def load(self, surveyId):
        keyId = self.SurveyFactoryClass.factory._filenameFromId(surveyId)
        return self.surveyFactory.load(keyId)


def main():
    srv = SurveyService()
    srv.storagePath = "/tmp"
    print [ x.id for x in srv.list() ]

if __name__ == "__main__":
    main()
