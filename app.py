#!/usr/bin/python
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import wsgi
import finder
import threading
from cherrypy import wsgiserver

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


t = threading.Thread(target=finder.Finder('config', os.environ['MX_USER'], os.environ['MX_PASSWORD']).run)
t.daemon = True
t.start()

server = wsgiserver.CherryPyWSGIServer((ip, port), wsgi.application, server_name=host_name)
server.start()
