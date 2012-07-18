import os
import subprocess
import inspect
import parsevalues
import xml.etree.cElementTree as etree

class BaseSlots(object):
    __slots__ = []
    def __init__(self, *args, **kwargs):
        allSlots = set()
        for cls in inspect.getmro(self.__class__):
            allSlots.update(getattr(cls, '__slots__', []))
        for slotName in allSlots:
            setattr(self, slotName, kwargs.get(slotName))

class EXECUTABLE(BaseSlots):
    __slots__ = [ 'name', 'execute', 'switches', 'results', 'stdout', 'stderr', 'returncode' ]
    def __repr__(self):
        return '%s' % self.name    
    @property
    def description(self):
        return ( "Name = %s\nExecutable = %s\nSwitches = %s\nResults = %s\n"
                "Stdout = %s\nStderr = %s\nReturnCode = %s\n" % 
                ('name', 'exec', 'results', 'switches', 'stdout', 'stderr', 'returncode'))

class Executioner(object):
    def __init__(self, scriptdir, values_xml):
        self.scriptdir = scriptdir
        self.scripts = []
        self.values_xml = values_xml

    def _errorXml(self, result):
        root = etree.Element(result.name)
        errors = etree.SubElement(root, 'errors')
        errors_name = etree.SubElement(errors, result.name)
        error_list = etree.SubElement(errors_name, 'error_list')
        error = etree.SubElement(error_list, 'error')
        etree.SubElement(error, 'code').text = "9999"
        detail = "%s %s %s" % (result.stdout,result.stderr,result.returncode)
        etree.SubElement(error, 'detail').text = detail
        etree.SubElement(error, 'message').text = "Error: Executable failed"
        etree.SubElement(error, 'success').text = "False"
        etree.SubElement(root, 'extensions')
        return root


    def _getEnviron(self):
        env = os.environ.copy()
        p = parsevalues.ValuesParser(self.values_xml)
        adds = p.parse()
        if adds:
            env.update(adds)
        return env

    def _getScripts(self, scriptdir):
        scripts = []
        if os.path.exists(scriptdir):
            scripts = [ EXECUTABLE(name=x, execute=os.path.join(scriptdir,x)) 
                            for x in os.listdir(scriptdir) 
                            if os.access(os.path.join(scriptdir, x), os.X_OK) ]
            scripts.sort()
        else:
            raise Exception
        return scripts

    def _runProcess(self, cmd, env, returncode=0):
        '''cmd @ [ '/sbin/service', 'name', 'status' ]'''
        #TODO mkdtemp;cd to tmp;execute;nuke tmpdir
        #TODO fix buffer issue with communicate
        try:
            proc = subprocess.Popen(cmd, shell=False, stdin=None,
                        stdout=subprocess.PIPE , stderr=subprocess.PIPE,
                        env=env)
            stdout, stderr = proc.communicate()        
            proc.poll()
            if proc.returncode:
                returncode = proc.returncode
            return stdout.decode("UTF8"), stderr.decode("UTF8"), returncode
        except Exception, ex:
            return ex

    def _execute(self, script):
        env = self._getEnviron()
        switches = ''
        if script.switches:
            switches = str(script.switches)
        cmd = [ script.execute, switches]
        script.stdout, script.stderr, script.returncode = self._runProcess(cmd, env)
        return script

    def execute(self):
        scripts = self._getScripts(self.scriptdir)
        results = []
        for script in scripts:
            results.append(self._execute(script))
        return results

    def toxml(self):
        xml = etree.Element('configurator')
        results = self.execute()
        for result in results:
            stub = self._errorXml(result)
            if result.stdout:
                try:
                    stub = etree.fromstring(result.stdout)
                except SyntaxError:
                    pass
            xml.append(stub)
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

