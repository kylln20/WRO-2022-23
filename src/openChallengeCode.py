import cv2
import time
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO
import serial
from readchar import readkey, key
from time import sleep

#initializing communication with the arduino
ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1) #approximately 115200 characters per second
ser.flush() #block the program until all the outgoing data has been sent

#setting up the pisugar button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

time.sleep(3)

#checks if the button was pressed: if it is, the program starts
while True:
    if GPIO.input(5) == GPIO.LOW:
        break

#default speed and angle of the RC car
speed = 1270
angle = 2060
prevAngle = 2060


#set up pi camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (800,600)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 80
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

#PID wall follow variables
proportional=0
error=0
prevError=0
target=0
diff=0
kd=0.0009
kp=-0.0012

#turning code variables
turning = False
prevTurn = " " 
prevBlue = False
currBlue = False
blueCount = 0

#frame rate counter
prevFrameTime = 0
newFrameTime = 0
fpsCount = 0


while True:
    #pi camera captures an image
    im= picam2.capture_array()

    # time when we finish processing for this frame
    new_frame_time = time.time()
    
    #the image is blurred for accuracy in the next step:
    #thresholding for the contours of the black walls
    imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imGray, (13, 13), 0)
    ret, imgThresh = cv2.threshold(imGray, 50, 255, cv2.THRESH_BINARY)
    v = np.median(imgBlur)
    lowThresh = int(max(0, (1.0 - 0.33) * v))
    highThresh = int(min(180, (1.0 + 0.33) * v))
    
    #previous image display for debugging purposes
    #imgRoi = cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2RGB)
    
    cv2.rectangle(imgRoi, (0, 250), (200, 600), (0, 255, 0), 2) #left
    cv2.rectangle(imgRoi, (600, 250), (800, 600), (0, 255, 0), 2) #right
    
    imgThresh = cv2.bitwise_not(imgThresh)

    #looking for the black contours in the thresholded image
    #the left wall and the right wall contours are searched for in different regions of interest
    leftContours, lefthierarchy = cv2.findContours(imgThresh[250:600, 0:200].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rightContours, righthierarchy = cv2.findContours(imgThresh[250:600, 600:800].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #looking for the largest black contour on the left side, aka the left wall
    maxLeftArea = 0
    leftArea = 0
    for i in leftContours:
        leftArea = cv2.contourArea(i)
        if leftArea > 300:
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(imgRoi, (x, y+250), (x+w, y+h+250), (0, 0, 255), 2)
            if leftArea > maxLeftArea:
                maxLeftArea = leftArea
    leftArea = maxLeftArea
    
    #same method is used for the right side
    maxRightArea = 0
    rightArea = 0
    for i in rightContours:
        rightArea = cv2.contourArea(i)
        if rightArea > 300:
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(imgRoi, (x+600, y+250), (x+w+600, y+h+250), (255, 0, 0), 2) 
            if rightArea > maxRightArea:
                maxRightArea = rightArea
    rightArea = maxRightArea
    
    #debugging output statements
    print("left area:", leftArea)
    print("right area:", rightArea)
    
        
    #PD wall following code
    #in the case that the robot doesn't need to turn:
    if(not turning):
        #based on the visible areas of the left and right walls:
        error = leftArea-rightArea
        proportional=(target - error)*kp
        diff=error-prevError
        print("proportional:", proportional)
        print("diff:", diff)
        motorSteering=proportional-(diff*kd)
        prevError=error
        #calculations are done using the P(roportional) D(erivative) formula to calculate how many degrees the robot should turn, motor steering
        print(motorSteering)
        #if motorSteering is within the physical limits of the servo, then it is applied
        if(motorSteering > -25 and motorSteering < 25):
            angle = 2060 + motorSteering
            angle = int(angle)
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
        elif(motorSteering > 25): #otherwise, if motorSteering is greater than 25 degrees, or less than -25 degrees, respective extremes are applied
            angle = 2085
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
        else:
            angle = 2035
            ser.write((str(angle)+"\n").encode('utf-8'))
            print("angle: ", angle)
    
    #turning code: based on the visible areas of the left and right wall
    #if too little of one wall is visible, that means the robot is approaching a corner and must turn
    if leftArea < 1000 and rightArea < 1500:
        if turning == True:
            if prevTurn == "left":
                print("turning left")
                angle = 2030
            elif prevTurn == "right":
                print("turning right")
                angle = 2090
    elif leftArea < 1000:
        if turning == False:
            print("turning left")
            turning = True
            angle = 2030
            prevTurn = "left"
    elif rightArea < 1500:
        if turning == False:
            print("turning right")
            turning = True
            angle = 2090
            prevTurn = "right"
    else:
        if turning == True:
            prevTurn = "none"
        turning = False

    #additional debugging code
    cv2.rectangle(imgRoi, (200, 260), (600, 260), (0, 255, 0), 2)

    #in the case where the robot is making a right turn from a 60cm path to another 60cm path
    #the above turning code does not perform consistently
    #thus, the code below checks if the robot approached too close to the wall
    num = 0
    for i in range(200, 600):
        if imgThresh[260][i] == 255:
            num = num+1
    print("wall percentage:", num/400.0)
    if num/400.0 > 0.70:
        closeToWall = True
    else:
        closeToWall = False
    print("close to wall:", closeToWall)

    #if it is the case that the robot is too close, and also the case that the above turning code has not worked
    #then the code below forces the robot to make a sharply angled turn to prevent hitting the wall
    if closeToWall and not turning:
        if rightArea < leftArea and rightArea < 5000:
            angle = 2095

    ser.write((str(angle) + "\n").encode('utf-8'))
    print("angle: ", angle)

            
    #counting laps code
    #the code counts laps based on the number of times it approaches the blue line at the corner of the mat
    #the code below, similar to the code to detect black walls, applies a filter to find the... 
    #...largest area of blue visible within the region of interest.
    img_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        
    lowerBlue = np.array([75, 50, 50])
    upperBlue = np.array([130, 255, 255])
    blueMask = cv2.inRange(img_hsv, lowerBlue, upperBlue)

    blueContours, blueHierarchy = cv2.findContours(blueMask[250:550, ], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    maxBlueArea = 0
    for i in blueContours:
        blueArea = cv2.contourArea(i)
        x, y, w, h = cv2.boundingRect(i)
        if blueArea > 2500:
            cv2.rectangle(imgRoi, (x, y), (x+w, y+h), (0, 0, 255), 2)
        if blueArea > maxBlueArea:
            maxBlueArea = blueArea

    #if the area exceeds a certain value (2500), then the robot is approaching the blue line
    if maxBlueArea > 2500:
        currBlue = True
    else: 
        currBlue = False
    #if previously, the camera could not detect blue and now it could, that indicates the robot is approaching the corner
    #by the same logic, if the camera could previously detect blue and then it can't, that indicates the robot is leaving the corner
    #in the two above scenarios, (prevBlue doesn't equal currBlue,) a counting number is increased. 
    #This counts the number of corners approached, as well as is later the indicator for the robot to stop.
    if not prevBlue == currBlue:
        blueCount = blueCount + 1
        if currBlue == True:
            turnTime = time.time()
    print("count of blue: ", blueCount)
    if blueCount % 2 == 0 and prevBlue != currBlue:
        prevDiff = 0
        prevTurn = " "
    prevBlue = currBlue

    
    ### show all regions of interest / contours
    #cv2.imshow("colours!", imgRoi)
    
    #stopping mechanism
    #an additional check for when the robot must turn is here
    #turnTime is constantly updated while blueCount is equal to 23, 
    #which stops once the robot leaves the corner and blueCount becomes 24
    if blueCount == 23:
        turnTime = time.time()
    endTurnTime = time.time()

    #a final check for when the robot must turn, the camera looks for 
    #how much of an area is black, and if that percentage is high enough, 
    #it means that the robot is approaching the next corner after the ending zone
    countblack = 0
    for i in range(250, 501):
        if imgThresh[200][i] == 255:
            countblack += 1
    countblack = countblack / 250
    print(countblack)

    #if the robot is close enough to the next corner, it has made 24/2 = 12 turns,
    #and it's been 1.2 seconds since it left the last corner, then the robot is to stop
    if countblack < 0.10 and blueCount >= 24 and endTurnTime-turnTime >= 1.2:
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
        
    speed = 1310
    ser.write((str(speed) + "\n").encode('utf-8'))
    print("speed: ", speed)
    
    
    #stops the bot if the frame rate begins to lag, to prevent crashing into the wall
    newFrameTime = time.time()
    fps = 1.0/(newFrameTime-prevFrameTime)
    prevFrameTime = newFrameTime
    fps = int(fps)
    print("fps: ", fps)
    if fps == 0:
        fpsCount = fpsCount + 1
    if fpsCount == 5:
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        angle = 2060
        ser.write((str(angle) + "\n").encode('utf-8'))
        print("angle: ", angle)
        break
    
    """
    #stop the program code
    if cv2.waitKey(1)==ord('q'):#wait until key ‘q’ pressed
        speed = 1500
        ser.write((str(speed) + "\n").encode('utf-8'))
        print("speed: ", speed)
        
        #angle = 2060
        #ser.write((str(angle) + "\n").encode('utf-8'))
        #print("angle: ", angle)
        break
    """
    #cv2.imshow("colours!", imgRoi)
        
cv2.destroyAllWindows()
