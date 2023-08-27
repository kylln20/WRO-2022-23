# ꕤ✿✧ *Engineering Documentation* ✧✿ꕤ

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

This document contains materials of Team [blank]'s self driving vehicle from Canada, particiapating in the WRO Future Engineers competition in the 2023 season.

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

## Table of Contents

+ **Repository Contents**
  
+ **Robot Mechanical Design**
+ **Robot Electrical design**
+ **Software Design**
+ **Design Choices**
+ **Open Challenge Strategy**
+ **Obstacle Challenge Strategy**
+ **Parts List**

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

## Respository Contents
𓆩♡𓆪 [Models](https://github.com/kylln20/WRO-2022-23/tree/main/models) | This folder contains all 3D printed models used | ✦

𓆩♡𓆪 [Schemes](https://github.com/kylln20/WRO-2022-23/tree/main/schemes) | This folder contains the electrical chematics of the vehicle | ✦

𓆩♡𓆪 [SRC](https://github.com/kylln20/WRO-2022-23/tree/main/src) | Programming and software is housed here | ✦

𓆩♡𓆪 [T-Photos](https://github.com/kylln20/WRO-2022-23/tree/main/t-photos) | Team member photos can be seen here | ✦

𓆩♡𓆪 [V-Photos](https://github.com/kylln20/WRO-2022-23/tree/main/v-photos) | Photos of the vehicle from all required sides can be seen here | ✦

𓆩♡𓆪 [Video](https://github.com/kylln20/WRO-2022-23/tree/main/video) | Youtube link is here for you to watch our vehicle work! | ✦

𓆩♡𓆪 [Other](https://github.com/kylln20/WRO-2022-23/tree/main/other) | Other essential materials or documentation regarding our vehicle | ✦

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
## ✧ Robot Mechanical Design ✧
  The vehicle is based off the white Traxxas Ford Bronco with adjusted motors and electrical systems. We used 3D-printed parts and EV3 lego parts to aid in holding our vehicle together. The original esc and motor have been replaced with a custom made esc we soddered and a motor we bought from the same suppliers as the Bronco. We removed the cover, front and back bumper, extra lights, and the suspension mechanism from the base Bronco. With the 3D printed board we put all our parts on top of it.
## ✧ Robot Electrical Design ✧
  Primarily working using its two "brains" the Master Raspberry pi and the slave arduion, out vehicle moves with signals sent between the two. The arduino has control over the DC and servo motor which control the movement and steering respectively using pulse-with-modulation. The raspberry pi has control over our camera and sends signals to the arduino based off the detection system we have coded, these signals help steer the vehicle in the right direction. (Refer to circuit sheet?)
## ✧ Software Design ✧
  Because our vehicle functions with both a Raspberry Pi and Arduino board, our code runs on two seperate languages. With the Arduino IDE software we coded our arduino board in c++ to take commands from the Raspberry Pi, these commands will dictate the Servo and Dc motor's movement and thus the vehichle's movement. As the main brain of our vehicle, the Raspberry Pi runs on python and works by using its camera to dictate how the vehicle should move.
## ✧ Design choies ✧
  Using the base of the traxxas, our first plan consisted of a fully 3d printed design using it as a chasis. 3D printing was hard to come by so we ended up mixing a bunch of materials together. We still use a 2d pirnted base but instead we have adhesives and glues to stick it and our lego parts together.
## ✧ Open Challenge Strategy ✧
  For the Open Challenge, we decided to take frames recorded from our camera and filter out so the black walls were highlighted. We then use regions of interest to help wall-follow and to help determine when to turn. With a PD following system we can fine tune the driving and turning so that our vehicle wll procede smoothly.
## ✧ Obstacle Challenge strategy ✧
    NA?

## ✧ Parts List ✧
+ TRA97074-1 Traxxas TRX-4M Ford Bronco 1/18 RTR 4X4 Trail Truck, White | [Link](https://www.bigboyswithcooltoys.ca/products/tra97074-1-traxxas-trx-4m-ford-bronco-1-18-rtr-4x4-trail-truck-white)
+ Lego Mindstorm Ev3 Core Set | [Link](https://www.amazon.com/Lego-Mindstorm-Ev3-Core-45544/dp/B00DEA55Z8)
+ Super Start Kit UNO R3 Project | [Link](https://www.amazon.ca/Elegoo-Project-Starter-Tutorial-Arduino/dp/B01D8KOZF4)
+ Raspberry Pi 4B | [Link](https://www.pishop.ca/product/raspberry-pi-4-model-b-2gb/?src=raspberrypi)
+ Double Switches
+ Hot Glue + Hot glue gun
+ Raspberry Pi FIsheye Camera | [Link](https://www.amazon.com/Raspberry-Camera-Module-160FOV-Fisheye/dp/B083XMGSVP/ref=sr_1_3?keywords=raspberry%2Bpi%2Bwide%2Bangle%2Bcamera&qid=1680461882&sr=8-3&th=1)
