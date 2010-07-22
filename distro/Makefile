#
# Copyright (c) 2010 rPath, Inc.
#
# All Rights Reserved
#

.PHONY: all install

all: default-all

install: default-install
	install -D -m0644 ractivaterc $(DESTDIR)/etc/conary/ractivate/ractivaterc
	install -D -m0755 ractivate.init $(DESTDIR)/etc/init.d/ractivate
	mkdir $(DESTDIR)/etc/conary/ractivate/config.d
	chmod 755 $(DESTDIR)/etc/conary/ractivate/config.d

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
