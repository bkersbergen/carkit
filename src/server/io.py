import keyboard
from collections import deque


class KeyboardIO(object):

    def __init__(self):
        self._keyboard_events = deque(maxlen=2)
        self._scan_code_mapping = {72: 'UP', 80: 'DOWN', 75: 'LEFT', 77: 'RIGHT'}
        self._throttle_events = set(['UP', 'DOWN'])
        self._steering_events = set(['LEFT', 'RIGHT'])
        self._steering_angle = 90
        self._throttle = 0
        self.enable_keyboard_listener()

    def get_throttle_and_steering(self):
        event1 = None
        event2 = None
        try:
            event1 = self._keyboard_events.pop()
            event2 = self._keyboard_events[0]
        except IndexError:
            pass
        if not event1:
            return self._throttle, self._steering_angle
        if event1 in self._throttle_events:
            if event1 == 'UP':
                self._throttle = self._throttle + 15
            else:
                self._throttle = self._throttle - 15
        if event1 in self._throttle_events and event2 and event2 in self._steering_events:
            if event2 == 'LEFT':
                self._steering_angle = self._steering_angle - 5
            else:
                self._steering_angle = self._steering_angle + 5
        if event1 in self._steering_events:
            if event1 == 'LEFT':
                self._steering_angle = self._steering_angle - 5
            else:
                self._steering_angle = self._steering_angle + 5
        if event1 in self._steering_events and event2 and event2 not in self._steering_events:
            if event1 == 'UP':
                self._throttle = self._throttle + 15
            else:
                self._throttle = self._throttle - 15
        return self._throttle, self._steering_angle

    def __handle_keyboard_event(self, event):
        action = self._scan_code_mapping.get(event.scan_code)
        if action:
            self._keyboard_events.append(action)

    def enable_keyboard_listener(self):
        keyboard.hook(self.__handle_keyboard_event)

    def disable_keyboard_listener(self):
        keyboard.unhook(self.__handle_keyboard_event)

