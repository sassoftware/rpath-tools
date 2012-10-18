#
# Copyright (c) 2012 rPath, Inc.
#

import os
import subprocess
import inspect
import parsevalues
import traceback
import uuid
import tempfile
import shutil

from lxml import etree

xsdFilePath = "/usr/conary/share/rpath-tools/xml_resources/xsd"

class BaseSlots(object):
    __slots__ = []
    def __init__(self, *args, **kwargs):
        allSlots = set()
        for cls in inspect.getmro(self.__class__):
            allSlots.update(getattr(cls, '__slots__', []))
        for slotName in allSlots:
            setattr(self, slotName, kwargs.get(slotName))

class EXECUTABLE(BaseSlots):
    __slots__ = [ 'name', 'type', 'execute', 'switches', 'results', 'stdout', 'stderr', 'returncode' ]
    def __repr__(self):
        return '%s' % self.name    
    @property
    def description(self):
        return ( "Name = %s\nConfigurator Type = %s\nExecutable = %s\nSwitches = %s\nResults = %s\n"
                "Stdout = %s\nStderr = %s\nReturnCode = %s\n" % 
                ('name', 'type', 'exec', 'results', 'switches', 'stdout', 'stderr', 'returncode'))
    def getdetails(self):
        return ("Stdout = %s\nStderr = %s\nReturnCode = %s\n" % 
                (self.stdout, self.stderr, self.returncode))

class Executioner(object):
    def __init__(self, configurator, scriptdir, values_xml, errtemplate):
        self.scriptdir = scriptdir
        self.scripts = []
        self.values_xml = values_xml
        self.errtemplate = errtemplate
        self.configurator = configurator
        self.xsdattrib = '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'


    def _validate(self, xml, xsd):
        xsdfile = os.path.join(xsdFilePath,  xsd)
        xmlschema_doc = etree.parse(xsdfile)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(xml)
        except etree.DocumentInvalid, ex:
            msg = "%s\n"  % str(ex.error_log)
            msg += traceback.format_exc()
            return False, msg, 70
        return True, '', 0

    def _sanitize(self, results):
        from xml.sax.saxutils import escape
        return escape(results)

    def _errorXml(self, result):
        error_name = 'config_error-%s' % uuid.uuid1()
        template = open(self.errtemplate).read()
        template = template.replace('__name__',error_name)
        template = template.replace('__display_name__',result.name)
        template = template.replace('__summary__','%s %s type configurator' % (result.execute, result.type))
        template = template.replace('__details__','Output from %s' % result.execute)
        template = template.replace('__error_code__',str(result.returncode))
        template = template.replace('__error_details__',self._sanitize(result.getdetails()))
        template = template.replace('__error_summary__',result.name)
        error_xml = etree.fromstring(template)
        return error_xml


    def _getEnviron(self):
        env = {}
        env['PATH'] = os.environ.get('PATH', '/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin')
        if os.path.exists(self.values_xml):
            p = parsevalues.ValuesParser(self.values_xml)
            adds = p.parse()
            if adds:
                env.update(adds)
        return env

    def _getTmpDir(self, pre):
        return tempfile.mkdtemp(prefix=pre)

    def _removeTmpDir(self, tmpdir):
        return shutil.rmtree(tmpdir)

    def _getScripts(self, scriptdir):
        scripts = []
        if os.path.exists(scriptdir):
            scripts = [ EXECUTABLE(name=x, execute=os.path.join(scriptdir,x), type=self.configurator) 
                            for x in sorted(os.listdir(scriptdir))
                            if os.access(os.path.join(scriptdir, x), os.X_OK) ]
            scripts.sort()
        else:
            raise Exception
        return scripts

    def _runProcess(self, cmd, env, tmpdir=None):
        try:
            proc = subprocess.Popen(cmd, shell=False, stdin=None,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    cwd=tmpdir, env=env)
            stdout, stderr = proc.communicate()
            return stdout.decode("UTF8"), stderr.decode("UTF8"), proc.returncode
        except Exception, ex:
            msg = "Failed to execute script: %s\n" % str(ex)
            msg += traceback.format_exc()
            return '', msg, 70

    def _execute(self, script):
        env = self._getEnviron()
        switches = ''
        if script.switches:
            switches = str(script.switches)
        cmd = [script.execute, switches]
        tempdir =  self._getTmpDir('rpath-')
        script.stdout, script.stderr, script.returncode = self._runProcess(cmd, env, tempdir)
        if not script.returncode:
            self._removeTmpDir(tempdir)
        return script

    def execute(self):
        scripts = self._getScripts(self.scriptdir)
        results = []
        for script in scripts:
            results.append(self._execute(script))
        return results

    def toxml(self):
        xml = etree.Element(self.configurator)
        # Do not run configurator if values.xml missing.
        if os.path.exists(self.values_xml):
            results = self.execute()
            for result in results:
                xsd = 'rpath-configurator-2.0.xsd'
                myxml = None
                if result.stdout:
                    try:
                        myxml = etree.fromstring(result.stdout)
                    except SyntaxError, ex:
                        #TODO add ex to error somehow... maybe?
                        xml.append(self._errorXml(result))
                    if myxml is not None:
                        # get xsd from xml if possible
                        if myxml.attrib and self.xsdattrib in myxml.attrib:
                            xsd = myxml.attrib[self.xsdattrib].split()[-1]
                        result.results, result.stderr, result.returncode = self._validate(myxml, xsd)
                        if result.results:
                            xml.append(myxml)
                        else:
                            xml.append(self._errorXml(result))
                else:
                    xml.append(self._errorXml(result))
        return xml

    def tostdout(self):
        xml = self.toxml()
        print etree.tostring(xml)

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

    #executer = Executioner('/usr/lib/rpath-tools/write.d', '/var/lib/rpath-tools/values.xml')
    #executer = Executioner('/usr/lib/rpath-tools/read.d', '/var/lib/rpath-tools/values.xml')
    #executer = Executioner('/usr/lib/rpath-tools/validate.d', '/var/lib/rpath-tools/values.xml')
    #executer = Executioner('/usr/lib/rpath-tools/discover.d', '/var/lib/rpath-tools/values.xml')

    #executer.execute()
    #executer.toxml()

