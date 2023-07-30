 #include <Keyboard.h>
 #include <Servo.h>



Servo BLDCMotor;
Servo servoMotor;

void setup(){
  Serial.begin(9600);
  servoMotor.attach(9);
  servoMotor.write(90);
  BLDCMotor.attach(9, 1000, 2000);
  BLDCMotor.writeMicroseconds(1500);

  Keyboard.begin();
}

void loop(){

  // check for incoming serial data:

  if (Serial.available() > 0) {

    // read incoming serial data:

    char inChar = Serial.read();

    if(inChar=="W"){
      BLDCMotor.writeMicroseconds(1000);
    }
    if(inChar=="S"){
      BLDCMotor.writeMicroseconds(2000);
    }
  }
 }
