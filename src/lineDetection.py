import cv2
import time
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO

#set up pisugar button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#checks if button was pressed
while True:
    if GPIO.input(5) == GPIO.LOW:
        break

#pixels
height = 0
dist = 0
distA = 0

#roi coordinates
points = [[0, 0], [0, 479], [799, 479], [799, 0]]

#set up pi camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (800,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 60 #this thing
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

while True:
    im= picam2.capture_array()
    #im = im[240:480, 0:800]

    # time when we finish processing for this frame
    new_frame_time = time.time()
    
    #use edge detection on image
    imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    imBlur = cv2.GaussianBlur(imGray, (13, 13), 0)
    ret, imgThresh = cv2.threshold(imGray, 90, 255, cv2.THRESH_BINARY)
    v = np.median(imBlur)
    lowThresh = int(max(0, (1.0 - 0.33) * v))
    highThresh = int(min(180, (1.0 + 0.33) * v))
    
    imgCanny = cv2.Canny(imgThresh, lowThresh, highThresh)
    cv2.imshow("grayscale + blur", imBlur) #blurred image that edge detection is used on
    #cv2.imshow("canny",imgCanny) #image with edge detection
    cv2.imshow("thresh",imgThresh)
    print(imgCanny) #printing out the colour
    #for finding the distance to the wall, using trig with the height of the wall and camera combined with the angle could work
    #when it comes to detecting the wall, due to the angle the camera is mounted we just move until it detects something lmao
    
    #this could be a good band-aid fix
    #while(not imgThresh):
        #code to ve
    #else if(condition for pillars):
        #code for the case
    
#     for i in range(0, 480):
#         if imgCanny[0][i] == 255:
#             points[0][1] = i
#             break
#     for i in range(0, 480):
#         if imgCanny[639][i] == 255:
#             points[3][1] = i
#             break
    #find bottom most white pixel, where track starts
# 
#     for i in range(479, -1, -1):
#         if imgCanny[i][0] == 255:
#             print(i)
#             break
#     for i in range(479, -1, -1):
#         if imgCanny[i][799] == 255:
#             print(i)
#             break


     
    if cv2.waitKey(1)==ord('q'):#wait until key ‘q’ pressed
        break
cv2.destroyAllWindows()
