#!/usr/bin/python

from utils import client

c = client.Client('https://admin:tclmeSRS@dhcp222.rdu.rpath.com/api/products')
print c.request()
