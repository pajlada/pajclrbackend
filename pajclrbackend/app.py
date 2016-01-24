#!/usr/bin/env python3

import socketio
import eventlet
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)

class BaseClient:
    client_type = 'BASE'

    def __init__(self, host):
        self.host = host

class CLRClient(BaseClient):
    client_type = 'CLR'

class HostClient(BaseClient):
    client_type = 'HOST'

clients = {}

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/host')
def roleplay_as_host():
    return render_template('host.html')

def add_client(sid, client):
    clients[sid] = client

def remove_client(sid):
    try:
        del clients[sid]
    except KeyError:
        # this should never occur ;-)
        print('whyyyyyyyyyyyyy')

@sio.on('connect', namespace='/host')
def connect_host(sid, environ):
    add_client(sid, HostClient(environ['REMOTE_ADDR']))
    print('Host Client connected {}-{}'.format(sid, environ['REMOTE_ADDR']))

@sio.on('connect', namespace='/clr')
def connect_clr(sid, environ):
    add_client(sid, CLRClient(environ['REMOTE_ADDR']))
    print('CLR Client connected {}-{}'.format(sid, environ['REMOTE_ADDR']))

@sio.on('disconnect')
def disconnect(sid):
    remove_client(sid)
    print('Client disconnected {}'.format(sid))

if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 2351)), app)
