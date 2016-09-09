#!/usr/bin/python

import os
import sys

import GumTreeFinder
import OLXFinder
from FinderThread import FinderThread

reload(sys)
sys.setdefaultencoding('utf-8')
import FlatFinder
import cherrypy
from cherrypy import wsgiserver

OLX = None
GumTree = None

if os.environ.has_key('OPENSHIFT_PYTHON_IP'):
    sys.path.insert(0, os.path.dirname(__file__))
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass

    ip = os.environ['OPENSHIFT_PYTHON_IP']
    port = int(os.environ['OPENSHIFT_PYTHON_PORT'])
    host_name = os.environ['OPENSHIFT_GEAR_DNS']
    data_dir = os.environ['OPENSHIFT_DATA_DIR']
    GumTree = GumTreeFinder.GumTreeFinder(data_dir, 'config_gumtree', os.environ['MX_USER'], os.environ['MX_PASSWORD'])
    OLX = OLXFinder.OLXFinder(data_dir, 'config_olx', os.environ['MX_USER'], os.environ['MX_PASSWORD'])


else:
    ip = '127.0.0.1'
    port = 8080
    host_name = 'localhost'
    data_dir = './data/'
    GumTree = GumTreeFinder.GumTreeFinder(data_dir, 'config_gumtree')
    OLX = OLXFinder.OLXFinder(data_dir, 'config_olx')

OLXThread = FinderThread(OLX)
GumTreeThread = FinderThread(GumTree)

OLXThread.start()
GumTreeThread.start()

wsgiapp = cherrypy.Application(FlatFinder.FlatFinder(data_dir, {'olx': OLXThread, 'gumtree': GumTreeThread}), '/')
server = wsgiserver.CherryPyWSGIServer((ip, port), wsgiapp, server_name=host_name)
server.start()

# cherrypy.server.socket_host = ip
# cherrypy.server.socket_port = port
# cherrypy.quickstart(FlatFinder)
