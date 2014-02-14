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


.PHONY: all install

all: default-all

install: default-install
ifndef LIB_ONLY
	install -D -m0644 rpathrc $(DESTDIR)/etc/conary/rpath-tools/rpathrc
	if  [ -f /etc/SuSE-release ]; then \
		install -D -m0755 postinstall.init.sles $(DESTDIR)$(initdir)/rpath-tools-postinstall; \
	else \
		install -D -m0755 postinstall.init.redhat $(DESTDIR)$(initdir)/rpath-tools-postinstall; \
	fi
	mkdir -p $(DESTDIR)/etc/conary/rpath-tools/config.d
	chmod 755 $(DESTDIR)/etc/conary/rpath-tools/config.d
	mkdir -p $(DESTDIR)/usr/lib/rpath-tools/postinstall.d
	mkdir -p $(DESTDIR)/var/lib/rpath-tools/postinstall.lock
	install -D -m0644 postinstall.tagdescription $(DESTDIR)/etc/conary/tags/postinstall
	install -D -m0755 postinstall.taghandler $(DESTDIR)/usr/libexec/conary/tags/postinstall
endif

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
