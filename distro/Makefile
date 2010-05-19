#
# Copyright (c) 2010 rPath, Inc.
#
# All Rights Reserved
#

.PHONY: all install

all: default-all

install: default-install
	install -D -m0644 activation $(DESTDIR)/etc/conary/config.d/activation

include ../Make.rules
include ../Make.defs
# vim: set sts=8 sw=8 noexpandtab :

