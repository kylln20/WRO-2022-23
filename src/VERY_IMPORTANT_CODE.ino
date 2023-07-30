#include <Servo.h>

Servo BLDCMotor;
Servo servoMotor;
char inputs[5];
int input;

void setup(){
  Serial.begin(9600);
  servoMotor.attach(9);
  servoMotor.write(90);
  BLDCMotor.attach(10, 1000, 2000);
  BLDCMotor.writeMicroseconds(1500);
}

void loop(){

  // check for incoming serial data:
  if (Serial.available() > 0) {
    // read incoming serial data:

    Serial.readBytesUntil('\n', inputs, 5);
    inputs[4] = '\0';
    delay(40);
    input = atoi(inputs);
    Serial.println(input);
    if(input >= 2025 && input <= 2095){
      Serial.println("Servo command");
      servoMotor.write(input-2000);
    }
    if(input <= 1600 && input >= 1300){
      Serial.println("Motor command");
      BLDCMotor.writeMicroseconds(input);
    }
  }
 }
