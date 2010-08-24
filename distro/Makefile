#
# Copyright (c) 2010 rPath, Inc.
#
# All Rights Reserved
#

.PHONY: all install

all: default-all

install: default-install
	install -D -m0644 registerrc $(DESTDIR)/etc/conary/rpath-tools/registerrc
	install -D -m0755 rpath-tools.init $(DESTDIR)/etc/init.d/rpath-tools
	mkdir $(DESTDIR)/etc/conary/rpath-tools/config.d
	chmod 755 $(DESTDIR)/etc/conary/rpath-tools/config.d

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
