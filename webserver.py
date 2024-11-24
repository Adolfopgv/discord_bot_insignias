from wsgiref.simple_server import make_server

def application(environ, start_response):
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response('200 OK', headers)
    return ['Server is running!'.encode('utf-8')]

def start_server():
    server = make_server('localhost', 8000, application)
    server.serve_forever()