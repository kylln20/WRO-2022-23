#!/usr/bin/env python3
import serial
from readchar import readkey, key
from time import sleep

if __name__ == '__main__':
    '''
    timeout: this is a timeout for read operations. Here we set it to 1 second. 
    It means that when we read from Serial, the program won’t be stuck forever if the data is not coming. 
    After 1 second or reading, if not all bytes are received, the function will return the already received bytes.
    '''
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1) #approximately 960 characters per second
    ser.flush() #block the program until all the outgoing data has been sent
    speed = 1390
    angle = 2060
    while True:
        k = readkey()
        
        if k == "w":
            if(speed > 1300):
                speed -= 5  #speed up
            ser.write((str(speed) + "\n").encode('utf-8'))
            print("speed: ", speed)
            
        if k == "x":
            if (speed < 1600):
                speed += 5  #slow down
            ser.write((str(speed) + "\n").encode('utf-8'))
            print("speed: ", speed)
           
        if k == key.SPACE:
            speed = 1500
            ser.write((str(speed) + "\n").encode('utf-8'))
            print("speed: ", speed)
        
        if k == "a":
            if(angle < 2095): #2090 + 45
                angle += 5  #turn left
            ser.write((str(angle) + "\n").encode('utf-8'))
            print("angle: ", angle)
            
        if k == "d":
            if(angle > 2025): #2090 - 45
                angle -= 5  #turn right
            ser.write((str(angle) + "\n").encode('utf-8'))
            print("angle: ", angle)
        
        if k == "s":
            angle = 2060
            ser.write((str(angle) + "\n").encode('utf-8'))
            print("angle: ", angle)
    
        sleep(0.01)
        
        if k == "q":
            speed = 1500
            ser.write((str(speed) + "\n").encode('utf-8'))
            print("speed: ", speed)
            
            angle = 2060
            ser.write((str(angle) + "\n").encode('utf-8'))
            print("angle: ", angle)
            break
