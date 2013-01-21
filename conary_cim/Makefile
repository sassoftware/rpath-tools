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

PROVIDERS = $(filter-out __init__.py,$(wildcard *.py))
PROVIDERS_PYC = $(addsuffix c,$(PROVIDERS))
PYCIM_DIR = /usr/lib/pycim
DATA_DIR = /var/lib/conary-cim/storage

POWERON_SCRIPTS_DIR = /etc/vmware-tools/scripts/poweron-vm-default.d
RESUME_SCRIPTS_DIR = /etc/vmware-tools/scripts/resume-vm-default.d

SFCB_CONF_DIR = /opt/vmware/etc/sfcb

all: $(PROVIDERS_PYC)

%.pyc: %.py
	python -c "import compileall; compileall.compile_dir('.', ddir='$(PYCIM_DIR)', quiet = True)"

install: install-code install-mof install-scripts install-conf install-data install-init

install-init: $(DESTDIR)$(INIT_DIR)
	install -m755 conary-cim.init $(DESTDIR)$(initdir)/conary-cim

install-code: $(DESTDIR)$(PYCIM_DIR) $(PROVIDERS_PYC)
	install -m644 $(PROVIDERS) $(PROVIDERS_PYC) $(DESTDIR)$(PYCIM_DIR)

install-mof:
	$(MAKE) -C mof install

install-scripts: $(DESTDIR)$(POWERON_SCRIPTS_DIR) $(DESTDIR)$(RESUME_SCRIPTS_DIR)
	install -m755 guestinfo-poweron.sh $(DESTDIR)$(POWERON_SCRIPTS_DIR)
	install -m755 guestinfo-resume.sh $(DESTDIR)$(RESUME_SCRIPTS_DIR)

install-conf: $(DESTDIR)$(SFCB_CONF_DIR)
	install -m644 sfcb.cfg $^

install-data: $(DESTDIR)$(DATA_DIR)

$(DESTDIR)$(PYCIM_DIR) $(DESTDIR)$(POWERON_SCRIPTS_DIR) $(DESTDIR)$(RESUME_SCRIPTS_DIR) $(DESTDIR)$(SFCB_CONF_DIR) $(DESTDIR)$(DATA_DIR) $(DESTDIR)$(initdir):
	install -d -m 755 $@

clean:
	@rm -rf *.pyc

include ../Make.defs
