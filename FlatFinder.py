import os
import cherrypy
from jinja import Environment, FileSystemLoader


class FlatFinder(object):
    def __init__(self, path, thread):
        self.path = path
        self.finder_thread = thread
        self.env = Environment(loader=FileSystemLoader('html'))
        self.password = 'passwd'

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
        if password == self.password:
            with open(self.path + 'config', 'w') as config:
                config.write(code)
            success = True
            self.finder_thread.restart()

        tmpl = self.env.get_template('config.html')
        config = ''
        with open(self.path + 'config', 'r') as config:
            config = config.read()
        return tmpl.render(config=config, success=success)
