import time
import socketio
from camera.carcam import CarCam
import base64
import os
import cv2
from picar import front_wheels, back_wheels

import picar

bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels(debug=True)
picar.setup()
bw.speed = 0
fw.offset = 0
#####################################################
# CLIENT

sio = socketio.Client()

start_timer = None


my_carcam = CarCam()


def send_telemetry():
    global start_timer
    start_timer = time.time()
    image_data = my_carcam.read()
    img_b64 = base64.b64encode(cv2.imencode('.jpg', image_data)[1]).decode()
    sio.emit('telemetry', {'image': img_b64, 'speed': 0, '_throttle': 0, '_steering_angle': 0})


@sio.on('connect')
def connect():
    send_telemetry()

@sio.on('disconnect')
def disconnect():
    print('Client disconnected')


@sio.on('steer')
def handle_steer(msg):
    global start_timer
    global bw
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    # Set speed content, and speed level content
    # Set speed content, and speed level content
    MAX_SPEED = 100
    MIN_SPEED = 40
    SPEED_LEVEL_1 = MIN_SPEED
    SPEED_LEVEL_2 = (MAX_SPEED - MIN_SPEED) / 4 * 1 + MIN_SPEED
    SPEED_LEVEL_3 = (MAX_SPEED - MIN_SPEED) / 4 * 2 + MIN_SPEED
    SPEED_LEVEL_4 = (MAX_SPEED - MIN_SPEED) / 4 * 3 + MIN_SPEED
    SPEED_LEVEL_5 = MAX_SPEED
    SPEED = [0, SPEED_LEVEL_1, SPEED_LEVEL_2, SPEED_LEVEL_3, SPEED_LEVEL_4, SPEED_LEVEL_5]
    # start handle throttle
    if msg['_throttle']:
        throttle = msg['_throttle'] // 4
    else:
        throttle = 0
    bw.speed = abs(throttle)
    if throttle < 0:
        bw.backward()
    else:
        bw.forward()
    # end handle throttle
    # start handle steering
    if msg['_steering_angle']:
        if msg['_steering_angle'] > 0:
            fw.turn_right()
        elif msg['_steering_angle'] < 0:
            fw.turn_left()
    else:
        fw.turn_straight()
    # end handle steering





    # sio.sleep(1)
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

