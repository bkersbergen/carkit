import cv2

class CarCam(object):
    def __init__(self):
        self.camera = cv2.VideoCapture(-1)
        # my camera only works with CV2 in this resolution
        self.camera.set(3, 480)
        self.camera.set(4, 360)

    def read(self):
        _, image = self.camera.read()
        return image

    def show_image_in_window(self):
        while self.camera.isOpened():
            _, image = self.camera.read()
            cv2.imshow('my carcam', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

