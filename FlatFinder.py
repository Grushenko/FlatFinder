import os


def wsgi(environ, start_response):
    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value)
                         for key, value in sorted(environ.items())]
        response_body = '\n'.join(response_body)
    else:
        ctype = 'text/html'
        response_body = ''
        found = ''
        with open('html/index.html', 'r') as html:
            response_body = html.read()
        with open(os.environ['OPENSHIFT_DATA_DIR']+'found.txt', 'r') as html:
            found = html.read()

        response_body.replace('{{body}}', found)

    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
    start_response(status, response_headers)
    return [response_body]