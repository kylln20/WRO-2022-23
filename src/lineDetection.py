import cv2
import time
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO
import serial
from readchar import readkey, key
from time import sleep

ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1) #approximately 115200 characters per second
ser.flush() #block the program until all the outgoing data has been sent


#set up pisugar button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#checks if button was pressed

while True:
    if GPIO.input(5) == GPIO.LOW:
        break

#1370
speed = 1300
angle = 2060
ser.write((str(speed) + "\n").encode('utf-8'))
print("speed: ", speed)
ser.write((str(angle) + "\n").encode('utf-8'))
print("angle: ", angle)
            
#roi coordinates
points = [(180, 160), (0, 320), (799, 320), (620, 160)]

#set up pi camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (800,600)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 80
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


proportional=0
error=0
prevError=0
target=0
diff=0
kd=0
kp=-0.0012

turning = False
#prevTurn = " "

prevFrameTime = 0
newFrameTime = 0

fpsCount = 0

while True:
    im= picam2.capture_array()

    # time when we finish processing for this frame
    new_frame_time = time.time()
    
    #use edge detection on image
    imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imGray, (13, 13), 0)
    ret, imgThresh = cv2.threshold(imGray, 50, 255, cv2.THRESH_BINARY)
    v = np.median(imgBlur)
    lowThresh = int(max(0, (1.0 - 0.33) * v))
    highThresh = int(min(180, (1.0 + 0.33) * v))
    
    #cv2.imshow("grayscale + blur", imBlur) #blurred image that edge detection is used on
    #cv2.imshow("thresh",imgThresh)
    
    imgRoi = cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2RGB)
    """
    imgRoi = cv2.line(imgRoi, points[0], points[1], (0, 155, 0), 4)
    imgRoi = cv2.line(imgRoi, points[1], points[2], (0, 155, 0), 4)
    imgRoi = cv2.line(imgRoi, points[2], points[3], (0, 155, 0), 4)
    imgRoi = cv2.line(imgRoi, points[3], points[0], (0, 155, 0), 4)
    imgRoi = cv2.line(imgRoi, (200, 200), (600, 200), (0, 155, 0), 4)
    """
    #cv2.imshow("region of interest", imgRoi)

    """
    #perspective warping
    width = 800
    height = 600
    original = np.float32(points)
    new = np.float32([(0, 0), (0, height-1), (width-1, height-1), (width-1,0)])
 
    grid = cv2.getPerspectiveTransform(original, new)
    imgPerspective = cv2.warpPerspective(imgThresh, grid, (width, height), cv2.INTER_LINEAR, borderMode = cv2.BORDER_CONSTANT, borderValue = (0,0,0))
    #imgPerspective = cv2.warpPerspective(imgRoi, grid, (width, height), cv2.INTER_LINEAR, borderMode = cv2.BORDER_CONSTANT, borderValue = (0,0,0))
    imgPerspectiveRGB = cv2.cvtColor(imgPerspective, cv2.COLOR_GRAY2RGB)
    
    #cv2.imshow("perspective", imgPerspective)
    
    
    ####new regions of interest
    """
    cv2.rectangle(imgRoi, (0, 250), (200, 600), (0, 255, 0), 2) #left
    cv2.rectangle(imgRoi, (600, 250), (800, 600), (0, 255, 0), 2) #right
    
    #keep car going straight
    ## initial contour detection
    #contours, hierarchy = cv2.findContours(imgInversePerspective, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print(len(contours))
    
    imgThresh = cv2.bitwise_not(imgThresh)

    leftContours, lefthierarchy = cv2.findContours(imgThresh[250:600, 0:200].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rightContours, righthierarchy = cv2.findContours(imgThresh[250: 600, 600: 800].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    maxLeftArea = 0
    leftArea = 0
    for i in leftContours:
        leftArea = cv2.contourArea(i)
        if leftArea > 300:
            x, y, w, h = cv2.boundingRect(i)
            #cv2.rectangle(imgPerspectiveRGB, (x, y+200), (x+w, y+h+200), (0, 0, 255), 2) #add crop offset 
            cv2.rectangle(imgRoi, (x, y+250), (x+w, y+h+250), (0, 0, 255), 2)
            if leftArea > maxLeftArea:
                maxLeftArea = leftArea
    leftArea = maxLeftArea
    
    
    maxRightArea = 0
    rightArea = 0
    for i in rightContours:
        rightArea = cv2.contourArea(i)
        if rightArea > 300:
            x, y, w, h = cv2.boundingRect(i)
            #cv2.rectangle(imgPerspectiveRGB, (x+600, y+200), (x+w+600, y+h+200), (255, 0, 0), 2)#add crop offset 
            cv2.rectangle(imgRoi, (x+600, y+250), (x+w+600, y+h+250), (255, 0, 0), 2) 
            if rightArea > maxRightArea:
                maxRightArea = rightArea
    rightArea = maxRightArea
    
    print("left area:", leftArea)
    print("right area:", rightArea)
    
    print("turning: ", turning)
    if(not turning):
        #pid linefollow
        error = leftArea-rightArea
        print("error: ", error)
        proportional=(target - error)*kp
        diff=error-prevError
        motorSteering=proportional+(diff*kd)
        prevError=error
        print(motorSteering)
        if(motorSteering > -25 and motorSteering < 25):
            angle = 2060 + motorSteering
            angle = int(angle)
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
        elif(motorSteering > 25):
            angle = 2085
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
        else:
            angle = 2035
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
        
        speed = 1300
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
    
    cv2.imshow("colours!", imgRoi)
    
    
    #check if should turn
    #num = 0
    #for i in range(200, 600):
    #    if imgThresh[200][i] == 255:
    #        num = num+1
    
    #if num/540.0 < 0.15:
    #    turning = True
    #    print("now turning")
    #    if(leftArea < rightArea):
    #        angle = 2035
    #        ser.write((str(angle) + "\n").encode('utf-8'))
    #        #print("angle: ", angle)
    #        speed = 1500
    #        ser.write((str(speed) + "\n").encode('utf-8'))
    #        #print("speed: ", speed)
    #    else:
    #        angle = 2085
    #        ser.write((str(angle) + "\n").encode('utf-8'))
    #        #print("angle: ", angle)
    #        speed = 1500
    #        ser.write((str(speed) + "\n").encode('utf-8'))
    #        #print("speed: ", speed)
    #else:
    #    turning = False
    
    
    #this shit is turning code
    if leftArea < 1000:
        print("turning left")
        turning = True
        angle = 2025
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        speed = 1300
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
    elif rightArea < 1000:
        print("turning right")
        turning = True
        angle = 2095
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        speed = 1300
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
    else:
        turning = False
        
    print(" ");
    
    newFrameTime = time.time()
    fps = 1.0/(newFrameTime-prevFrameTime)
    prevFrameTime = newFrameTime
    fps = int(fps)
    print("fps: ", fps)
    if fps == 0:
        fpsCount = fpsCount + 1
    if fpsCount == 10:
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
    
    if cv2.waitKey(1)==ord('q'):#wait until key ‘q’ pressed
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
        
cv2.destroyAllWindows()
