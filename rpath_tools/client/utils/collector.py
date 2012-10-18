import os
import time
import tempfile
import shutil
import subprocess
import tarfile
import inspect
import traceback

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


class FirstRun(object):
    def __init__(self):
        self.collectord = "/usr/lib/rpath-tools/collector.d"
        self.storage = "/var/lib/rpath-tools/collector"
        self.dirlist = [ self.collectord, self.storage ]
        self.default_tarlist = "default-tarlist"
        self.default_collector = "default-collector"

        self.tar_data = [ '/boot/grub/grub.conf',
                '/etc/conary/',
                '/etc/firewall',
                '/etc/fstab',
                '/etc/hosts',
                '/etc/resolv.conf',
                '/etc/sysconfig/',
                '/etc/sysctl.conf',
                '/tmp/conary-error-.*.txt',
                '/var/lib/conarydb/conarydb',
                '/var/log/conary',
                '/var/log/conary-cim.log',
                '/var/log/messages',
                '/var/log/rpath-tools.log', ]

        self.collector_data = [ '#!/bin/sh',
                'DIR=$(mktemp -d /tmp/collect-XXXXXX)',
                'cd $DIR',
                '#biosdecode > biosdecode 2>&1',
                'cat /proc/cmdline > proc-cmdline 2>&1',
                'cat /proc/meminfo > meminfo 2>&1',
                'cat /proc/partitions > partitions 2>&1',
                'chkconfig --list > chkconfig 2>&1',
                'conary config > conary-config 2>&1',
                'conary q --full-versions --flavors --troves > conaryq 2>&1',
                'conary q --info  | grep -B3 Pinned | grep -B3 True > conary-pinned  2>&1',
                'conary rblist --full-versions --flavors > conary-rblist 2>&1',
                'conary updateall --info --full-versions --flavors --debug=all > conary-update 2>&1',
                'conary updateall --items > conary-update-items 2>&1',
                'df > df 2>&1',
                'dmesg > dmesg 2>&1',
                'dmidecode > dmidecode 2>&1',
                'ip -6 route show > ip6route 2>&1',
                'ip addr show > ipaddr 2>&1',
                'ipcs > ipcs 2>&1',
                'ip route show > iproute 2>&1',
                'lspci -n > lspci-n 2>&1',
                'lspci -vvxxxx > lspci-vx 2>&1',
                'lsusb -v > lsusb 2>&1',
                'mount > mount 2>&1',
                'runlevel > runlevel 2>&1',
                'sysctl -A > sysctl 2>&1',
                'uname -a > uname 2>&1',
                'echo $DIR', ]

    def _mkdir(self, dirname):
        if not os.path.exists(dirname):
            try:
                os.mkdir(dirname)
            except Exception, ex:
                raise Exception, ex
        return dirname


    def _mkdirs(self):
        for dirname in self.dirlist:
            ret = self._mkdir(dirname)
            print "Creating %s" % ret

    def _writescript(self, script, data):
        if os.path.exists(os.path.dirname(script)):
            try:
                "Writing %s" % script
                f = open(script, 'w')
                for lx in data:
                    f.write(lx + '\n')
                f.close()
            except Exception, ex:
                raise Exception, ex
        if os.path.exists(script) and script.endswith('-collector'):
            "Making %s executable" % script
            os.chmod(script, 0755)
        return True

    def _writescripts(self):
        self._writescript(os.path.join(self.collectord, self.default_tarlist), self.tar_data)
        self._writescript(os.path.join(self.collectord, self.default_collector), self.collector_data)

    def create(self):
        self._mkdirs()
        self._writescripts()


class Collector(object):
    def __init__(self):
        self.collectord = "/usr/lib/rpath-tools/collector.d"
        self.storage = "/var/lib/rpath-tools/collector"
        self.default_tarlist = "default-tarlist"
        self.default_collector = "default-collector"

    def _chkStorageDir(self):
        if not os.path.exists(self.storage):
            try:
                os.mkdir(self.storage)
            except Exception, ex:
                raise Exception, ex
        return self.storage

    def _getEnviron(self):
        env = {}
        env['PATH'] = os.environ.get('PATH', '/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin')
        return env

    def _getTarFileList(self, tardir):
        scripts = []
        tarfiles = []
        if os.path.exists(tardir):
            scripts = [ os.path.join(tardir, x) for x in sorted(os.listdir(tardir)) if x.endswith('-tarlist') ]
        else:
            raise Exception
        for script in scripts:
            try:
                tarfiles = [ x.strip() for x in open(script, 'r').readlines() if os.path.exists(x.strip()) ]
            except Exception, ex:
                msg = "Failed to read script: %s\n" % str(ex)
                msg += traceback.format_exc()
                return '', msg, 70
        return tarfiles

    def _getScripts(self, scriptdir):
        scripts = []
        if os.path.exists(scriptdir):
            scripts = [ EXECUTABLE(name=x, execute=os.path.join(scriptdir,x))
                            for x in sorted(os.listdir(scriptdir))
                            if os.access(os.path.join(scriptdir, x), os.X_OK) ]
        else:
            raise Exception
        return scripts

    def _getTmpDir(self, pre):
        return tempfile.mkdtemp(prefix=pre)

    def _removeTmpDir(self, tmpdir):
        return shutil.rmtree(tmpdir)

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


    def _tarBall(self, name, filelist, pre='', rem=''):
        print "Creating %s" % name
        tar = tarfile.open(name, "w:gz")
        for filename in filelist:
            tar.add(filename, arcname=filename.replace(rem, pre))
        tar.close()
        print "Finished %s" % name
        return name

    def _getTarName(self, pre, filepath=None):
        name = '%s-%s' % (pre, int(time.time()))
        tar = '%s.tar.gz' % name
        if filepath:
            tar = os.path.join(filepath, tar)
        return tar, name

    def _execute(self, script, env, tmpdir):
        print "Executing %s" % script.execute
        cmd = [ script.execute ]
        script.stdout, script.stderr, script.returncode = self._runProcess(cmd, env, tmpdir)
        return script

    def execute(self, tmpdir):
        print "Processing scripts..."
        env = self._getEnviron()
        scripts = self._getScripts(self.collectord)
        results = []
        for script in scripts:
            results.append(self._execute(script, env, tmpdir))
        return results

    def collect(self):
        collectables = []
        tmpdir =  self._getTmpDir('collector-')
        print "Checking setup..."
        firstrun = FirstRun()
        firstrun.create()
        print "Starting collection %s" % tmpdir
        scripts = self.execute(tmpdir)
        for script in scripts:
            err = 0
            collectables = [ x.strip() for x in script.stdout.split(',') ]
            for collectable in collectables:
                if not os.path.isdir(collectable):
                    print "%s not a directory" % collectables.pop(collectable)
                    err += 1
            if err:
                print "ERROR with script %s" % script.name
                print "stdout %s\nstderr %s\nreturncode %s\n" % (script.stdout,
                        script.stderr, script.returncode)

        tarfilelist = self._getTarFileList(self.collectord)
        tarfile = self._tarBall(self._getTarName('collector', '/tmp/')[0], tarfilelist)
        if tarfile:
            collectables.append(tarfile)
        ctb, sctb = self._getTarName('rpath-collector', self._chkStorageDir())
        ctb_tarball = self._tarBall(ctb, collectables, sctb, '/tmp')
        if ctb_tarball:
            print "Removing %s" % tmpdir
            self._removeTmpDir(tmpdir)
        print "Collection : %s" % ctb_tarball
        return ctb_tarball


if __name__ == "__main__":
  collector = Collector()
  results = collector.collect()
  print results
