#!/usr/bin/python

import os
import sys

from FinderThread import FinderThread

reload(sys)
sys.setdefaultencoding('utf-8')
import FlatFinder
import finder
import threading
import cherrypy
from cherrypy import wsgiserver

find = None

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
    find = finder.Finder(data_dir, os.environ['MX_USER'], os.environ['MX_PASSWORD'])

else:
    ip = '127.0.0.1'
    port = 8080
    host_name = 'localhost'
    data_dir = './'
    find = finder.Finder(data_dir)

thread = FinderThread(find)
thread.start()

wsgiapp = cherrypy.Application(FlatFinder.FlatFinder(data_dir, thread), '/')
server = wsgiserver.CherryPyWSGIServer((ip, port), wsgiapp, server_name=host_name)
server.start()

# cherrypy.server.socket_host = ip
# cherrypy.server.socket_port = port
# cherrypy.quickstart(FlatFinder)
