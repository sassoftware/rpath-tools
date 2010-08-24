#
# Copyright (c) 2010 rPath, Inc.
#
# All Rights Reserved
#

.PHONY: all install

all: default-all

install: default-install
	install -D -m0644 rregisterrc $(DESTDIR)/etc/conary/ractivate/ractivaterc
	install -D -m0755 rregister.init $(DESTDIR)/etc/init.d/ractivate
	mkdir $(DESTDIR)/etc/conary/rregister/config.d
	chmod 755 $(DESTDIR)/etc/conary/rregister/config.d

clean: clean-subdirs default-clean

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :
