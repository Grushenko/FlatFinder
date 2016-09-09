import os
import cherrypy
from jinja import Environment, FileSystemLoader


class FlatFinder(object):
    def __init__(self, path):
        self.path = path
        self.env = Environment(loader=FileSystemLoader('html'))

    @cherrypy.expose
    def index(self):
        tmpl = self.env.get_template('index.html')
        found = ''
        with open(self.path + 'found.txt', 'r') as html:
            found = html.read()
        found = found.split('\n')
        return tmpl.render(found=found)

    @cherrypy.expose
    def config(self):
        tmpl = self.env.get_template('config.html')
        config = ''
        with open(self.path + 'config', 'r') as config:
            config = config.read()
        return tmpl.render(config=config)

    @cherrypy.expose
    def config_save(self, code, password):
        success = False
        if password == 'passwd':
            with open(self.path + 'config', 'w') as config:
                config.write(code)
            success = True
        tmpl = self.env.get_template('config.html')
        config = ''
        with open(self.path + 'config', 'r') as config:
            config = config.read()

        return tmpl.render(config=config, success=success)
