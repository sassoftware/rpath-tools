#
# Copyright (c) 2010 rPath, Inc.
#
# All Rights Reserved
#

.PHONY: all install

all: default-all

install: default-install
ifndef LIB_ONLY
	install -D -m0644 rpathrc $(DESTDIR)/etc/conary/rpath-tools/rpathrc
	if  [ -f /etc/SuSE-release ]; then \
		install -D -m0755 rpath-tools.init.sles $(DESTDIR)$(initdir)/rpath-tools; \
		install -D -m0755 postinstall.init.sles $(DESTDIR)$(initdir)/rpath-tools-postinstall; \
	else \
		install -D -m0755 rpath-tools.init.redhat $(DESTDIR)$(initdir)/rpath-tools; \
		install -D -m0755 postinstall.init.redhat $(DESTDIR)$(initdir)/rpath-tools-postinstall; \
	fi
	mkdir -p $(DESTDIR)/etc/conary/rpath-tools/config.d
	chmod 755 $(DESTDIR)/etc/conary/rpath-tools/config.d
	mkdir -p $(DESTDIR)/usr/lib/rpath-tools/{read,write,validate,discover,postinstall}.d
	mkdir -p $(DESTDIR)/var/lib/rpath-tools/postinstall.lock
	install -D -m0644 rpath-tools.cron $(DESTDIR)/etc/cron.d/rpath-tools.cron
	install -D -m0644 postinstall.tagdescription $(DESTDIR)/etc/conary/tags/postinstall
	install -D -m0755 postinstall.taghandler $(DESTDIR)/usr/libexec/conary/tags/postinstall
endif

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
