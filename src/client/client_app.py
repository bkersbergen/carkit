import time
import socketio
import json

#####################################################
# CLIENT

sio = socketio.Client()
start_timer = None
import os

def send_context_update():
    global start_timer
    start_timer = time.time()
    with open('images/my_image_file.jpg', 'rb') as f:
        image_data = f.read()
    sio.emit('context_update', {'image': image_data})
    print('client: send_context_update')


@sio.on('connect')
def connect():
    send_context_update()

@sio.on('disconnect')
def disconnect():
    print('Client disconnected')


@sio.on('action_update')
def handle_action_update(msg):
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    action = msg['action']
    print(action)
    sio.sleep(1)
    send_context_update()


def connect_to_server():
    sio.connect('http://localhost:5000')
    sio.wait()


if __name__ == '__main__':
    for i in range(0, 10):
        while True:
            try:
                connect_to_server()
            except socketio.exceptions.ConnectionError as ce:
                print('error:', ce)
            break
