import os
from jinja import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('html'))

def wsgi(environ, start_response):
        tmpl = env.get_template('index.html')
        found = ''
        with open(os.environ['OPENSHIFT_DATA_DIR']+'found.txt', 'r') as html:
            found = html.read()
        found = found.split('\n')
        response_body = tmpl.render(found=found)
        status = '200 OK'
        ctype = 'text/plain'
        response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]
