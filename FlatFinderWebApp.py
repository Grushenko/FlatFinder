import codecs
import os
import cherrypy
from jinja import Environment, FileSystemLoader


class FlatFinder(object):
    def __init__(self, path, thread):
        self.path = path
        self.finder_thread = thread
        self.env = Environment(loader=FileSystemLoader('html'))
        self.password = '<3<3<3<3<3'

    @cherrypy.expose
    def index(self, sort_by='date'):

        sorting_order = {'date': 1, 'name': 2, 'rooms': 5, 'price': 4, 'district': 3}

        tmpl = self.env.get_template('index.html')
        found = {'olx': [], 'gumtree': [], 'otodom': []}
        try:
            with codecs.open(self.path + 'found_olx.txt', 'r', 'utf-8') as html:
                for idx, row in enumerate(html.read().split('\n')):
                    if len(row):
                        r = row.split('|')
                        r.append(idx)
                        found['olx'].append(tuple(r))
        except:
            pass

        try:
            with codecs.open(self.path + 'found_gumtree.txt', 'r', 'utf-8') as html:
                for idx, row in enumerate(html.read().split('\n')):
                    if len(row):
                        r = row.split('|')
                        r.append(idx)
                        found['gumtree'].append(tuple(r))
        except:
            pass

        try:
            with codecs.open(self.path + 'found_otodom.txt', 'r', 'utf-8') as html:
                for idx, row in enumerate(html.read().split('\n')):
                    if len(row):
                        r = row.split('|')
                        r.append(idx)
                        found['otodom'].append(tuple(r))
        except:
            pass

        for data in found:
            found[data] = sorted(found[data], key=lambda key: key[sorting_order.get(sort_by, 1)])

        return tmpl.render(found=found)

    @cherrypy.expose
    def olx_update(self, value=None):
        if value:
            with codecs.open(self.path + 'found_olx.txt', 'a', 'utf-8') as log:
                log.write(value)
                log.write('\n')
            return value
        return 'No value!'

    @cherrypy.expose
    def otodom_update(self, value=None):
        if value:
            with codecs.open(self.path + 'found_otodom.txt', 'a', 'utf-8') as log:
                log.write(value)
                log.write('\n')
            return value
        return 'No value!'

    @cherrypy.expose
    def panel(self):
        tmpl = self.env.get_template('panel.html')
        return tmpl.render()

    @cherrypy.expose
    def config(self, config_file):
        tmpl = self.env.get_template('config.html')
        config = ''
        with open(self.path + config_file, 'r') as config:
            config = config.read()
        return tmpl.render(config=config, config_file=config_file)

    @cherrypy.expose
    def config_save(self, config_file, code, password):
        success = False
        if password == self.password:
            with open(self.path + config_file, 'w') as config:
                config.write(code)
            success = True
            if config_file == 'config_olx':
                self.finder_thread['olx'].restart()
            else:
                self.finder_thread['gumtree'].restart()

        tmpl = self.env.get_template('config.html')
        config = ''
        with open(self.path + config_file, 'r') as config:
            config = config.read()
        return tmpl.render(config=config, config_file=config_file, success=success)
