import time
import socketio
from camera.carcam import CarCam
import base64
import cv2

#####################################################
# CLIENT

sio = socketio.Client()
start_timer = None
import os

my_carcam = CarCam()

def send_telemetry():
    global start_timer
    start_timer = time.time()
    image_data = my_carcam.read()
    img_b64 = base64.b64encode(cv2.imencode('.jpg', image_data)[1]).decode()
    sio.emit('telemetry', {'image': img_b64, 'speed': 0, 'throttle': 0, 'steering_angle': 0})
    print('client: send_context_update')


@sio.on('connect')
def connect():
    send_telemetry()

@sio.on('disconnect')
def disconnect():
    print('Client disconnected')


@sio.on('steer')
def handle_steer(msg):
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    # steer = msg['steer']
    print(msg)
    sio.sleep(1)
    send_telemetry()


def connect_to_server():
    sio.connect('http://192.168.178.16:5000')
    sio.wait()


if __name__ == '__main__':
    for i in range(0, 10):
        while True:
            try:
                connect_to_server()
            except socketio.exceptions.ConnectionError as ce:
                print('error:', ce)
            break
