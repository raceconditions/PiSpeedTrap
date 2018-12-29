# CarSpeed Version 2.0

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from pathlib import Path
from pytz import timezone
import time
import math
import datetime
import cv2
import pytz
from client import getLicensePlateImage
import logging 
import sys
import os

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
logPath = "/tmp"
fileName = "carspeed"

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

# place a prompt on the displayed image
def prompt_on_image(txt):
    global image
    cv2.putText(image, txt, (10, 35),
    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
     
# calculate speed from pixels and time
def get_speed(pixels, ftperpixel, secs):
    if secs > 0.0:
        return ((pixels * ftperpixel)/ secs) * 0.681818  
    else:
        return 0.0
 
# calculate elapsed seconds
def secs_diff(endTime, begTime):
    diff = (endTime - begTime).total_seconds()
    return diff

# record speed in .csv format
def record_speed(res):
    global csvfileout
    f = open(csvfileout, 'a')
    f.write(res+"\n")
    f.close

# mouse callback function for drawing capture area
def draw_rectangle(event,x,y,flags,param):
    global ix,iy,fx,fy,drawing,setup_complete,image, org_image, prompt
 
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
 
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            image = org_image.copy()
            prompt_on_image(prompt)
            cv2.rectangle(image,(ix,iy),(x,y),(0,255,0),2)
  
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        fx,fy = x,y
        image = org_image.copy()
        prompt_on_image(prompt)
        cv2.rectangle(image,(ix,iy),(fx,fy),(0,255,0),2)

# define timezones
EASTERN = timezone('US/Eastern')
UTC = pytz.utc
        
# define some constants
DISTANCE = 83  #<---- enter your distance-to-road value here
MIN_SPEED = 15  #<---- enter the minimum speed for saving images
SAVE_CSV = True  #<---- record the results in .csv format in carspeed_(date).csv

THRESHOLD = 15
MIN_AREA = 1000
BLURSIZE = (15,15)
IMAGEWIDTH = 1640
IMAGEHEIGHT = 1232
RESOLUTION = [IMAGEWIDTH,IMAGEHEIGHT]
FOV = 62.2    #<---- Field of view
FPS = 30
SHOW_BOUNDS = True
SHOW_IMAGE = False

# hard coded monitor area
MONITOR_TOP_LEFT_X = 300
MONITOR_TOP_LEFT_Y = 600
MONITOR_BOT_RIGHT_X = 1340
MONITOR_BOT_RIGHT_Y = 900

# the following enumerated values are used to make the program more readable
WAITING = 0
TRACKING = 1
SAVING = 2
UNKNOWN = 0
LEFT_TO_RIGHT = 1
RIGHT_TO_LEFT = 2

# calculate the the width of the image at the distance specified
frame_width_ft = 2*(math.tan(math.radians(FOV*0.5))*DISTANCE)
ftperpixel = frame_width_ft / float(IMAGEWIDTH)
rootLogger.debug("Image width in feet {} at {} from camera".format("%.0f" % frame_width_ft,"%.0f" % DISTANCE))

# state maintains the state of the speed computation process
# if starts as WAITING
# the first motion detected sets it to TRACKING
 
# if it is tracking and no motion is found or the x value moves
# out of bounds, state is set to SAVING and the speed of the object
# is calculated
# initial_x holds the x value when motion was first detected
# last_x holds the last x value before tracking was was halted
# depending upon the direction of travel, the front of the
# vehicle is either at x, or at x+w 
# (tracking_end_time - tracking_start_time) is the elapsed time
# from these the speed is calculated and displayed 
 
state = WAITING
direction = UNKNOWN
initial_x = 0
last_x = 0
 
#-- other values used in program
base_image = None
abs_chg = 0
mph = 0
secs = 0.0
ix,iy = -1,-1
fx,fy = -1,-1
drawing = False
setup_complete = False
tracking = False
text_on_image = 'No cars'
prompt = ''

# initialize the camera. Adjust vflip and hflip to reflect your camera's orientation
camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = FPS
camera.vflip = False
camera.hflip = False
camera.exposure_mode = 'sports'

rawCapture = PiRGBArray(camera, size=camera.resolution)
# allow the camera to warm up
time.sleep(0.9)

# create an image window and place it in the upper left corner of the screen
#cv2.namedWindow("Speed Camera")
#cv2.moveWindow("Speed Camera", 10, 40)

# call the draw_rectangle routines when the mouse is used
#cv2.setMouseCallback('Speed Camera',draw_rectangle)
 
# grab a reference image to use for drawing the monitored area's boundry
camera.capture(rawCapture, format="bgr", use_video_port=True)
image = rawCapture.array
rawCapture.truncate(0)
org_image = image.copy()

if SAVE_CSV:
    csvfileout = "/var/www/images/carspeed.csv"
    if not Path("/var/www/images/carspeed.csv").is_file():
        record_speed('Date,Day,Time,Speed,Image')
else:
    csvfileout = ''

#prompt = "Define the monitored area - press 'c' to continue" 
# prompt_on_image(prompt)
 
# wait while the user draws the monitored area's boundry
#while not setup_complete:
    #cv2.imshow("Speed Camera",image)
 
    #wait for for c to be pressed  
#    key = cv2.waitKey(1) & 0xFF
  
    # if the `c` key is pressed, break from the loop
#    if key == ord("c"):
#        break

# the monitored area is defined, time to move on
#prompt = "Press 'q' to quit" 
 
# since the monitored area's bounding box could be drawn starting 
# from any corner, normalize the coordinates
 
if fx > ix:
    upper_left_x = ix
    lower_right_x = fx
else:
    upper_left_x = fx
    lower_right_x = ix
 
if fy > iy:
    upper_left_y = iy
    lower_right_y = fy
else:
    upper_left_y = fy
    lower_right_y = iy

upper_left_x = MONITOR_TOP_LEFT_X
lower_right_x = MONITOR_BOT_RIGHT_X
upper_left_y = MONITOR_TOP_LEFT_Y
lower_right_y = MONITOR_BOT_RIGHT_Y
     
monitored_width = lower_right_x - upper_left_x
monitored_height = lower_right_y - upper_left_y
 
rootLogger.debug("Monitored area:")
rootLogger.debug(" upper_left_x {}".format(upper_left_x))
rootLogger.debug(" upper_left_y {}".format(upper_left_y))
rootLogger.debug(" lower_right_x {}".format(lower_right_x))
rootLogger.debug(" lower_right_y {}".format(lower_right_y))
rootLogger.debug(" monitored_width {}".format(monitored_width))
rootLogger.debug(" monitored_height {}".format(monitored_height))
rootLogger.debug(" monitored_area {}".format(monitored_width * monitored_height))
 
# capture frames from the camera (using capture_continuous.
#   This keeps the picamera in capture mode - it doesn't need
#   to prep for each frame's capture.

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #initialize the timestamp
    timestamp = datetime.datetime.now()
 
    # grab the raw NumPy array representing the image 
    image = frame.array
 
    # crop area defined by [y1:y2,x1:x2]
    gray = image[upper_left_y:lower_right_y,upper_left_x:lower_right_x]
 
    # convert the fram to grayscale, and blur it
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, BLURSIZE, 0)
 
    # if the base image has not been defined, initialize it
    if base_image is None:
        base_image = gray.copy().astype("float")
        lastTime = timestamp
        rawCapture.truncate(0)
        #cv2.imshow("Speed Camera", image)
  
    # compute the absolute difference between the current image and
    # base image and then turn eveything lighter gray than THRESHOLD into
    # white
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(base_image))
    thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    
    # dilate the thresholded image to fill in any holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # look for motion 
    motion_found = False
    biggest_area = 0
 
    # examine the contours, looking for the largest one
    for c in cnts:
        (x1, y1, w1, h1) = cv2.boundingRect(c)
        # get an approximate area of the contour
        found_area = w1*h1 
        # find the largest bounding rectangle
        if (found_area > MIN_AREA) and (found_area > biggest_area):  
            biggest_area = found_area
            motion_found = True
            x = x1
            y = y1
            h = h1
            w = w1

    if motion_found:
        if state == WAITING:
            # intialize tracking
            state = TRACKING
            initial_x = x
            last_x = x
            initial_time = timestamp
            last_mph = 0
            text_on_image = 'Tracking'
            rootLogger.debug(text_on_image)
            rootLogger.debug("x-chg    Secs      MPH  x-pos width")
        else:
            # compute the lapsed time
            secs = secs_diff(timestamp,initial_time)

            if secs >= 15:
                state = WAITING
                direction = UNKNOWN
                text_on_image = 'No Car Detected'
                motion_found = False
                biggest_area = 0
                rawCapture.truncate(0)
                base_image = None
                rootLogger.debug('Resetting')
                continue             

            if state == TRACKING:       
                if x >= last_x:
                    direction = LEFT_TO_RIGHT
                    abs_chg = x + w - initial_x
                else:
                    direction = RIGHT_TO_LEFT
                    abs_chg = initial_x - x
                mph = get_speed(abs_chg,ftperpixel,secs)
                rootLogger.debug("{0:4d}  {1:7.2f}  {2:7.0f}   {3:4d}  {4:4d}".format(abs_chg,secs,mph,x,w))
                real_y = upper_left_y + y
                real_x = upper_left_x + x
                # is front of object outside the monitired boundary? Then write date, time and speed on image
                # and save it 
                if ((x <= 2) and (direction == RIGHT_TO_LEFT)) \
                        or ((x+w >= monitored_width - 2) \
                        and (direction == LEFT_TO_RIGHT)):
                    if (last_mph > MIN_SPEED):    # save the image
                        text_on_image = "Car detected at %s mph" % last_mph
                        # timestamp the image
                        currenttimestamp = datetime.datetime.now(UTC).astimezone(EASTERN)
                        cv2.putText(image, currenttimestamp.strftime("%A %d %B %Y %I:%M:%S%p %Z"),
                            (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
                        # write the speed: first get the size of the text
                        size, base = cv2.getTextSize( "%.0f mph" % last_mph, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
                        # then center it horizontally on the image
                        cntr_x = int((IMAGEWIDTH - size[0]) / 2) 
                        cv2.putText(image, "%.0f mph" % last_mph,
                            (cntr_x , int(IMAGEHEIGHT * 0.2)), cv2.FONT_HERSHEY_SIMPLEX, 2.00, (0, 255, 0), 3)
                        # and save the image to disk
                        # use the following image file name if you want to be able to sort the images by speed
                        dateFolder = "/var/www/images/" + currenttimestamp.strftime("%Y%m%d") + "/"
                        imageFilename = "car_at_%02.0f" % last_mph + "_" + currenttimestamp.strftime("%Y%m%d_%H%M%S%Z") + ".jpg"
                        if not os.path.exists(dateFolder):
                            os.makedirs(dateFolder)
                        cv2.imwrite(dateFolder + imageFilename,image)
                        try:
                            if (direction == RIGHT_TO_LEFT):
                                getLicensePlateImage(dateFolder + "car_at_%02.0f" % last_mph + "_" + currenttimestamp.strftime("%Y%m%d_%H%M%S%Z") + "_lic.jpg")
                        except Exception:
                            rootLogger.exception("Unable to get license plate image.")
                        if SAVE_CSV:
                            cap_time = currenttimestamp
                            record_speed(cap_time.strftime("%Y.%m.%d")+','+cap_time.strftime('%A')+','+\
                               cap_time.strftime('%H%M')+','+("%.0f" % last_mph) + ','+imageFilename)
                    state = SAVING
                # if the object hasn't reached the end of the monitored area, just remember the speed 
                # and its last position
                last_mph = mph
                last_x = x
    else:
        if state != WAITING:
            state = WAITING
            direction = UNKNOWN
            text_on_image = 'No Car Detected'
            rootLogger.debug(text_on_image)
            
    # only update image and wait for a keypress when waiting for a car
    # This is required since waitkey slows processing.
    if (state == WAITING):    
 
        # draw the text and timestamp on the frame
        cv2.putText(image, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
        cv2.putText(image, "Road Status: {}".format(text_on_image), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
     
        if SHOW_BOUNDS:
            #define the monitored area right and left boundary
            cv2.line(image,(upper_left_x,upper_left_y),(upper_left_x,lower_right_y),(0, 255, 0))
            cv2.line(image,(lower_right_x,upper_left_y),(lower_right_x,lower_right_y),(0, 255, 0))
       
        # show the frame and check for a keypress
        if SHOW_IMAGE:
            prompt_on_image(prompt)
            #cv2.imshow("Speed Camera", image)
            
        # Adjust the base_image as lighting changes through the day
        if state == WAITING:
            last_x = 0
            cv2.accumulateWeighted(gray, base_image, 0.25)
 
        state=WAITING;
        key = cv2.waitKey(1) & 0xFF
      
        # if the `q` key is pressed, break from the loop and terminate processing
        if key == ord("q"):
            break
         
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
  
# cleanup the camera and close any open windows
cv2.destroyAllWindows()

