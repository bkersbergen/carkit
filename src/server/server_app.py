# set async_mode to 'threading' (2000ms), 'eventlet' (13ms), 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's installed
async_mode = None

# roundtrip with 640x480px image takes 40ms.

import time
from flask import Flask
import socketio
import json
import os

sio = socketio.Server(logger=True, async_mode=async_mode, binary=True)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = '7jijasdof!9nasd!f!'
thread = None


@sio.on('context_update')
def handle_context_update_from_client(sid, msg):
    image_data = msg['image']
    print('Received message: ', image_data)
    sio.emit('action_update', {'action': 'l'})


if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi

        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi

        try:
            from geventwebsocket.handler import WebSocketHandler

            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file server_app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)
