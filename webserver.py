from wsgiref.simple_server import make_server
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

def application(environ, start_response):
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response('200 OK', headers)
    return ['Server is running!'.encode('utf-8')]

def start_server():
    try:
        server = make_server(HOST, PORT, application)
        print(f"Server running on {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Error starting the server: {e}")
