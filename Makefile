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


all: all-subdirs default-all

all-subdirs:
	for d in $(MAKEALLSUBDIRS); do make -C $$d DIR=$$d || exit 1; done

export TOPDIR = $(shell pwd)
export TIMESTAMP = $(shell python -c "import time; print time.time(); exit;")
export CFGDEVEL=rpathrc

SUBDIRS=rpath_tools distro commands
MAKEALLSUBDIRS=rpath_tools distro commands

extra_files = \
	Make.rules 		\
	Makefile		\
	Make.defs		\
	NEWS			\
	README			\
	LICENSE


.PHONY: clean dist install subdirs html

subdirs: default-subdirs

install: install-subdirs

clean: clean-subdirs default-clean

doc: html

html:
	ln -fs plugins/ rbuild_plugins
	scripts/generate_docs.sh
	rm -f rbuild_plugins

dist:
	if ! grep "^Changes in $(VERSION)" NEWS > /dev/null 2>&1; then \
		echo "no NEWS entry"; \
		exit 1; \
	fi
	$(MAKE) forcedist


archive:
	hg archive  --exclude .hgignore -t tbz2 rbuild-$(VERSION).tar.bz2

forcedist: archive

forcetag:
	hg tag -f rpath-tools-$(VERSION)

tag:
	hg tag rpath-tools-$(VERSION)

devel:
		mkdir -p devel/sfcb/clients
		mkdir devel/config.d
		rm -f devel/sfcb.cfg
		echo "sslClientTrustStore: $(TOPDIR)/devel/sfcb/clients" >> devel/sfcb.cfg
		echo "sslCertificateFilePath: $(TOPDIR)/devel/sfcb/server.pem" >> devel/sfcb.cfg
		echo "SERVER.PEM DATA" > devel/sfcb/server.pem
		rm -f $(CFGDEVEL)
		echo "topDir $(TOPDIR)/devel" >> $(CFGDEVEL)
		echo "generatedUuidFile generated-uuid" >> $(CFGDEVEL)
		echo "localUuidFile local-uuid" >> $(CFGDEVEL)
		echo "localUuidBackupDirectoryName old" >> $(CFGDEVEL)
		echo "sfcbConfigurationFile $(TOPDIR)/devel/sfcb.cfg" >> $(CFGDEVEL)
		echo "logFile $(TOPDIR)/devel/rpath-tools.log" >> $(CFGDEVEL)
		echo "debugMode True" >> $(CFGDEVEL)
		echo "registrationMethod direct" >> $(CFGDEVEL)
		echo "directMethod 127.0.0.1:8000" >> $(CFGDEVEL)
		echo "retrySlotTime 3" >> $(CFGDEVEL)
		echo "lastPollFileName $(TOPDIR)/devel/poll" >> $(CFGDEVEL)
		echo "lastRegistrationFileName $(TOPDIR)/devel/registration" >> $(CFGDEVEL)
		echo "registrationRetryCount 3" >> $(CFGDEVEL)
		echo "includeConfigFile $(TOPDIR)/devel/config.d/*" >> $(CFGDEVEL)
		echo "validateRemoteIdentity False" >> $(CFGDEVEL)
		echo "randomWaitFileName randomWait" >> $(CFGDEVEL)
		echo "conaryProxyFilePath $(TOPDIR)/devel/rpath-tools-conaryProxy" >> $(CFGDEVEL)
		echo "$(TIMESTAMP)" > $(TOPDIR)/devel/poll
		echo "$(TIMESTAMP)" > $(TOPDIR)/devel/registration
		echo 'sudo PYTHONPATH=$(TOPDIR):$(TOPDIR)/../../../rbuilder/claymore/include commands/rpath $$@' > rpath-devel
		chmod +x rpath-devel
        
clean-devel:
		sudo rm -rf devel
		rm -f $(CFGDEVEL)
		rm -f rpath-devel


clean: clean-devel clean-subdirs default-clean 

include Make.rules
include Make.defs
 
# vim: set sts=8 sw=8 noexpandtab :
