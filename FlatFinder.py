import os
import cherrypy
from jinja import Environment, FileSystemLoader


class FlatFinder(object):
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('html'))

    @cherrypy.expose
    def index(self):
        tmpl = self.env.get_template('index.html')
        found = ''
        with open(os.environ['OPENSHIFT_DATA_DIR'] + 'found.txt', 'r') as html:
            found = html.read()
        found = found.split('\n')
        return tmpl.render(found=found)

    @cherrypy.expose
    def config(self):
        tmpl = self.env.get_template('config.html')
        config = ''
        with open(os.environ['OPENSHIFT_DATA_DIR'] + 'config', 'r') as config:
            config = config.read()
        return tmpl.render(config=config)
