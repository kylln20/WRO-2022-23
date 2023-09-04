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
        
time.sleep(5)

#1270
speed = 1500
angle = 2060
#ser.write((str(speed) + "\n").encode('utf-8'))
#print("speed: ", speed)
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
kd=0.001
kp=-0.0012

kdo = 0
kpo = 0.08

turning = False
#prevTurn = " "

prevFrameTime = 0
newFrameTime = 0
fpsCount = 0

prevBlue = False
currBlue = False
blueCount = 0

obstacle = "none"
prevObstacle = "none"

xr,yr, wr, hr = 0, 0, 0, 0
xg, yg, wg, hg = 0, 0, 0, 0

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
    
    
    ####new regions of interest
    
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
    
    
    img_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    
    #red obstacle detection
    lowerBound = np.array([150, 30, 100])
    upperBound = np.array([180, 255, 255])
    colourMask = cv2.inRange(img_hsv, lowerBound, upperBound)
    redContours, redHierarchy = cv2.findContours(colourMask[100: 500, 50:750], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #green obstacle detection
    lowerBound = np.array([65, 60, 60])
    upperBound = np.array([90, 255, 255])
    colourMask = cv2.inRange(img_hsv, lowerBound, upperBound)
    greenContours, greenHierarchy = cv2.findContours(colourMask[100: 500, 50:750], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    maxRedArea = 0
    maxRedIndex = 0
    for i in redContours:
        redArea = cv2.contourArea(i)
        if redArea > maxRedArea and redArea > 300:
            maxRedArea = redArea
            maxRedIndex = i
            xr, yr, wr, hr = cv2.boundingRect(i)
            cv2.rectangle(imgRoi, (xr+50, yr+100), (xr+wr+50, yr+hr+100), (255, 0, 0), 2)


    maxGreenArea = 0
    maxGreenIndex = 0
    for i in greenContours:
        greenArea = cv2.contourArea(i)
        if greenArea > maxGreenArea and greenArea > 300:
            maxGreenArea = greenArea
            maxGreenIndex = i
            xg, yg, wg, hg = cv2.boundingRect(i)
            cv2.rectangle(imgRoi, (xg+50, yg+100), (xg+wg+50, yg+hg+100), (0, 255, 0), 2)

    if maxGreenArea > 300 and maxRedArea > 300:
        if yg+hg > yr+hr:
            obstacle = "green"
        else:
            obstacle = "red"
    elif maxGreenArea > 300:
        obstacle = "green"
    elif maxRedArea > 300:
        obstacle = "red"
    else:
        obstacle = "none"
    print("obstacle:", obstacle)
    
    if prevObstacle != obstacle:
        prevError = 0
    
    if turning:
        if obstacle == "red":
            target = 200
            error = xr + wr - target
            print("error:", error)
            #print("red:", xr+wr)
            diff = error - prevError
            proportional = error*kpo
            print("proportional:", proportional)
            motorSteering = proportional-(diff*kdo)
            prevError = error
            prevObstacle = obstacle
        elif obstacle == "green":
            target = 550 #x coordinate of green block
            error = xg - target
            print("error:", error)
            #print("green:", xg)
            diff = error - prevError
            proportional = error*kpo
            print("proportional:", proportional)
            motorSteering = proportional-(diff*kdo)
            prevError = error
            prevObstacle = obstacle
        elif obstacle == "none":
            #pid linefollow
            print("target: ", target)
            error = leftArea-rightArea
            print("error: ", error)
            proportional=(target - error)*kp
            diff=error-prevError
            motorSteering=proportional-(diff*kd)
            prevError=error
        
        print("motor angle:", motorSteering)
        
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
    else: #turning states
        #check which direction is turning in
        if leftArea < 900 and rightArea < 900:
                if turning == True:
                    if prevTurn == "left":
                        print("turning left")
                    elif prevTurn == "right":
                        print("turning right")
            elif leftArea < 900:
                if turning == False:
                    print("turning left")
                    turning = True
                    prevTurn = "left"
            elif rightArea < 900:
                if turning == False:
                    print("turning right")
                    turning = True
                    prevTurn = "right"
            else:
                if turning == True:
                    prevTurn = "none"
                turning = False
        #then based on obstacle, do stuff
        if obstacle == "red":
            if prevTurn == "left":
                #check front wall, if close, then sharp turn
                #else, then don't yet turn
            elif prevTurn == "right":
                #sharp turn
        elif obstacle == "green":
            if prevTurn == "left":
                #sharp turn
            elif prevTurn == "right":
                #check front wall, if close, then sharp turn
                #else, then don't yet turn
        else:
            if prevTurn == "left":
                angle = 2030
            elif prevTurn == "right":
                angle = 2090
    
    
    speed = 1500
    ser.write((str(speed) + "\n").encode('utf-8'))
    print("speed: ", speed)
            
            
    #counting laps code
        
    lowerBlue = np.array([95, 30, 140])
    upperBlue = np.array([130, 255, 255])
    blueMask = cv2.inRange(img_hsv, lowerBlue, upperBlue)

    blueContours, blueHierarchy = cv2.findContours(blueMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    maxBlueArea = 0
    for i in blueContours:
        blueArea = cv2.contourArea(i)
        x, y, w, h = cv2.boundingRect(i)
        if blueArea > 3000:
            cv2.rectangle(imgRoi, (x, y), (x+w, y+h), (0, 0, 255), 2)
        if blueArea > maxBlueArea:
            maxBlueArea = blueArea
            
    if maxBlueArea > 3000:
        currBlue = True
        turning = True
    else: 
        currBlue = False
    #print("prev blue:", prevBlue)
    #print("curr blue:", currBlue)
    #print("max blue area:", maxBlueArea)
    if not prevBlue == currBlue:
        blueCount = blueCount + 1
    print("count of blue: ", blueCount)
    prevBlue = currBlue
    
    print(" ")
    
    
    ### show all regions of interest / contours
    cv2.imshow("colours!", imgRoi)
    if blueCount == 23:
        lastTurnTime = time.time()
        
    if blueCount == 24:
        #delay( to be changed)
        #newTurnTime = time.time()
        #if newTurnTime - lastTurnTime > :
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
    
    #frame rate ded code
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
    
    
    #stop the program code
    if cv2.waitKey(1)==ord('q'):#wait until key ‘q’ pressed
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
    
    
        
cv2.destroyAllWindows()