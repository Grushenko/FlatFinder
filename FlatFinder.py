import os
from jinja import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('html'))

def wsgi(environ, start_response):
        tmpl = env.get_template('index.html')
        found = ''
        with open(os.environ['OPENSHIFT_DATA_DIR']+'found.txt', 'r') as html:
            found = html.read()
        found = found.split('\n')
        return tmpl.render(found=found)

