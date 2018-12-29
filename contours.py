from picamera.array import PiRGBArray
from picamera import PiCamera
import sys
import time
import picamera
import cv2
import numpy as np

THRESHOLD = 15
MIN_AREA = 350
BLURSIZE = (15,15)
IMAGEWIDTH = 1640
IMAGEHEIGHT = 1232
RESOLUTION = [IMAGEWIDTH,IMAGEHEIGHT]
FOV = 62.2    #<---- Field of view
FPS = 30

MONITOR_TOP_LEFT_X = 240
MONITOR_TOP_LEFT_Y = 600
MONITOR_BOT_RIGHT_X = 1400
MONITOR_BOT_RIGHT_Y = 900

upper_left_x = MONITOR_TOP_LEFT_X
lower_right_x = MONITOR_BOT_RIGHT_X
upper_left_y = MONITOR_TOP_LEFT_Y
lower_right_y = MONITOR_BOT_RIGHT_Y

base_image = None

with picamera.PiCamera() as camera:
    camera.resolution = RESOLUTION
    camera.vflip = False
    camera.hflip = False
    camera.start_preview()
    time.sleep(2)
    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        image = stream.array

        # crop area defined by [y1:y2,x1:x2]
        gray = image[upper_left_y:lower_right_y,upper_left_x:lower_right_x]
        # convert the fram to grayscale, and blur it
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, BLURSIZE, 0)
    
        # if the base image has not been defined, initialize it
        if base_image is None:
            base_image = gray.copy().astype("float")
    
        # compute the absolute difference between the current image and
        # base image and then turn eveything lighter gray than THRESHOLD into
        # white
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(base_image))
        thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    
        # dilate the thresholded image to fill in any holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        print(cnts)
