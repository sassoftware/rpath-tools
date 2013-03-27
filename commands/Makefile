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


TOPDIR=..

bin_files = rpath rpath-register rpath-hardware rpath-config rpath-iconfig rpath-scanner rpath-configurator rpath-tmpwatch rpath-collector

extra_dist = Makefile


all: default-all 
	mkdir -p $(TOPDIR)/bin
	install -m755 rpath $(TOPDIR)/bin/rpath
	install -m755 rpath-register $(TOPDIR)/bin/rpath-register
	install -m755 rpath-hardware $(TOPDIR)/bin/rpath-hardware
	install -m755 rpath-config $(TOPDIR)/bin/rpath-config
	install -m755 rpath-iconfig $(TOPDIR)/bin/rpath-iconfig
	install -m755 rpath-scanner $(TOPDIR)/bin/rpath-scanner
	install -m755 rpath-configurator $(TOPDIR)/bin/rpath-configurator
	install -m755 rpath-tmpwatch $(TOPDIR)/bin/rpath-tmpwatch
	install -m755 rpath-collector $(TOPDIR)/bin/rpath-collector
	install -m755 rpath-informer $(TOPDIR)/bin/rpath-informer

install:
ifndef LIB_ONLY
	mkdir -p $(DESTDIR)$(bindir)
	for f in $(bin_files); do \
		install -m755 $$f $(DESTDIR)$(bindir)/$$f; \
	done
	for f in $(sbin_files); do \
		install -m755 $$f $(DESTDIR)$(sbindir)/$$f; \
	done
endif

dist: default-dist

clean: default-clean
	rm -rf $(TOPDIR)/bin

include $(TOPDIR)/Make.rules
include $(TOPDIR)/Make.defs
