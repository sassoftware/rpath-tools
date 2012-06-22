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
		install -D -m0755 rpath-tools.init.sles $(DESTDIR)/etc/init.d/rpath-tools; \
	else \
		install -D -m0755 rpath-tools.init.redhat $(DESTDIR)/etc/init.d/rpath-tools; \
	fi
	mkdir -p $(DESTDIR)/etc/conary/rpath-tools/config.d
	chmod 755 $(DESTDIR)/etc/conary/rpath-tools/config.d
	install -D -m0644 rpath-tools.cron $(DESTDIR)/etc/cron.d/rpath-tools.cron
endif

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
