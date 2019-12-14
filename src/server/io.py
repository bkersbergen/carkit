import keyboard
from collections import deque


class KeyboardIO(object):

    def __init__(self):
        self._keyboard_events = deque(maxlen=2)
        self._scan_code_mapping = {72: 'UP', 80: 'DOWN', 75: 'LEFT', 77: 'RIGHT'}
        self._throttle_events = {'UP': 100, 'DOWN': -100}
        self._steering_events = {'LEFT': -100, 'RIGHT': 100}
        keyboard.hook(self.__handle_keyboard_event)
        # keyboard.unhook(self.__handle_keyboard_event)  # removes the hook

    def get_throttle_and_steering(self):
        event1 = None
        event2 = None
        try:
            event1 = self._keyboard_events.pop()
            event2 = self._keyboard_events[0]
        except IndexError:
            pass
        throttle = None
        steering = None
        if not event1:
            return throttle, steering
        if event1 in self._throttle_events:
            throttle = self._throttle_events.get(event1)
        if event1 in self._throttle_events and event2 and event2 in self._steering_events:
            steering = self._steering_events.get(event2)
        if event1 in self._steering_events:
            steering = self._steering_events.get(event1)
        if event1 in self._steering_events and event2 and event2 not in self._steering_events:
            throttle = self._throttle_events.get(event2)
        return throttle, steering

    def __handle_keyboard_event(self, event):
        action = self._scan_code_mapping.get(event.scan_code)
        if action:
            self._keyboard_events.append(action)

