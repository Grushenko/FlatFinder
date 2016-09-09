#!/usr/bin/python
import codecs
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import ConfigParser

import cherrypy
from cherrypy import wsgiserver

from GumTreeFinder import GumTreeFinder
from OLXFinder import OLXFinder
from FinderThread import FinderThread
import FlatFinderWebApp

# OPENSHIFT
if 'OPENSHIFT_PYTHON_IP' in os.environ:
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
else:
    if len(sys.argv) == 2:
        ip = sys.argv[0]
        port = sys.argv[1]
        host_name = sys.argv[0] + ':' + sys.argv[1]
        data_dir = '../data/'
    else:
        ip = '127.0.0.1'
        port = 8080
        host_name = 'localhost'
        data_dir = './data/'

cred_conf = ConfigParser.RawConfigParser()
cred_conf.readfp(codecs.open(data_dir + 'credentials', 'r', 'utf-8'))
mx_user = cred_conf.get('mx', 'mx_user')
mx_password = cred_conf.get('mx', 'mx_password')

GumTree = GumTreeFinder(data_dir, 'config_gumtree', mx_user, mx_password)
GumTreeThread = FinderThread(GumTree)
GumTreeThread.start()

OLXThread = None
# OLX = OLXFinder(data_dir, 'config_olx', mx_user, mx_password)
# OLXThread = FinderThread(OLX)
# OLXThread.start()

wsgi_app = cherrypy.Application(FlatFinderWebApp.FlatFinder(data_dir, {'olx': OLXThread, 'gumtree': GumTreeThread}),
                                '/')
server = wsgiserver.CherryPyWSGIServer((ip, port), wsgi_app, server_name=host_name)
server.start()
