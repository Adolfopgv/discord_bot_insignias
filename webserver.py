from wsgiref.simple_server import make_server
import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT") or 8000

def application(environ, start_response):
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response('200 OK', headers)
    return ['Server is running!'.encode('utf-8')]

def start_server():
    server = make_server(HOST, PORT, application)
    server.serve_forever()