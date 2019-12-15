import time
import socketio
from camera.carcam import CarCam
import base64
import sys
import cv2
from picarlib.front_wheels import Front_Wheels
from picarlib.back_wheels import Back_Wheels
import picarlib

bw = Back_Wheels(debug=True)
fw = Front_Wheels(debug=True)
picarlib.setup()
bw.speed = 0
fw.offset = 0

#####################################################
# CLIENT

sio = socketio.Client()

start_timer = None


my_carcam = CarCam()


def send_telemetry():
    global start_timer
    global bw, fw
    start_timer = time.time()
    image_data = my_carcam.read()
    img_b64 = base64.b64encode(cv2.imencode('.jpg', image_data)[1]).decode()
    sio.emit('telemetry', {'image': img_b64, 'speed': bw.speed, '_throttle': 0, '_steering_angle': fw.angle})


@sio.on('connect')
def connect():
    send_telemetry()

@sio.on('disconnect')
def disconnect():
    print('Client disconnected, stopping car')
    global picarlib, fw, bw
    bw.speed = 0
    bw.backward()
    fw.turn_straight()
    picarlib.setup()


@sio.on('steer')
def handle_steer(msg):
    global start_timer
    global bw
    global fw
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    # start handle throttle
    if msg['_speed']:
        if msg['_speed'] > 0:  # did I mount the servo's in the car in opposite direction?
            bw.backward()
        else:
            bw.forward()
        bw.speed = abs(msg['_speed'])
    # end handle throttle
    # start handle steering
    if msg['_steering_angle']:
        fw.turn(msg['_steering_angle'])
    # end handle steering
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

