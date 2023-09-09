#include <Servo.h>

//declaring variables

//DC Motor
Servo BLDCMotor;

//Servo Motor
Servo servoMotor;

//take in input from the raspberry pi
char inputs[5];

//the 
int input;

void setup(){
  //the serial communication with the raspberry pi is started
  Serial.begin(115200);
  //the pins to which the two motors are connected are declared
  //and the motors are initialized with starting values
  servoMotor.attach(9);
  servoMotor.write(90);
  BLDCMotor.attach(10, 1000, 2000);
  BLDCMotor.writeMicroseconds(1500);
}

void loop(){
  // check for incoming serial data:
  if (Serial.available() > 0) {
    // read incoming serial data:
    Serial.readBytes(inputs, 5);
    inputs[4] = '\0';
    input = atoi(inputs);
    //Serial.println(input);
    if(input >= 2025 && input <= 2095){
      //Servo command
      servoMotor.write(input-2000);
    }
    if(input <= 1600 && input >= 1100){
      //Motor command
      BLDCMotor.writeMicroseconds(input);
    }
  }
 }
