
/*
 Stepper Motor Control - one step at a time

 This program drives a unipolar or bipolar stepper motor.
 The motor is attached to digital pins 8 - 11 of the Arduino.

 The motor will step one step at a time, very slowly.  You can use this to
 test that you've got the four wires of your stepper wired to the correct
 pins. If wired correctly, all steps should be in the same direction.

 Use this also to count the number of steps per revolution of your motor,
 if you don't know it.  Then plug that number into the oneRevolution
 example to see if you got it right.

 Created 30 Nov. 2009
 by Tom Igoe

 */

#include <Stepper.h>

const int stepsPerRevolution = 200;  // change this to fit the number of steps per revolution
// for your motor

// initialize the stepper library on pins 8 through 11:
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);


int stepCount = 0;         // number of steps the motor has taken
char last_state = 1;

void setup() {
  // initialize the serial port:
  Serial.begin(9600);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(4,OUTPUT);
  pinMode(5,INPUT_PULLUP);
  digitalWrite(4,LOW);
  digitalWrite(12,HIGH);
  digitalWrite(13,HIGH);
  myStepper.setSpeed(10);
}

void loop() {

  static  char newInputChar;
/*  
  if ((last_state==1) && (digitalRead(5)==LOW)){
    Serial.println("Went LOW");
    last_state = 0;
  }
  else if ((last_state==0) && (digitalRead(5)==HIGH)){
    Serial.println("Went HIGH");
    last_state=1;
  }
  */
  while (Serial.available() > 0)
  {
    newInputChar = Serial.read();
    if (newInputChar == 'r') {
      stepCount = 0;
    }
    else {
      if (newInputChar == 'a') {
        digitalWrite(12,HIGH);
        digitalWrite(13,HIGH);
        myStepper.step(2);
        stepCount++;
      }
      else if (newInputChar == 'b') {
        digitalWrite(12,HIGH);
        digitalWrite(13,HIGH);
        myStepper.step(-2);
        stepCount--;
      }
        delay(300);
  //      digitalWrite(8,LOW);
  //      digitalWrite(9,LOW);
  //      digitalWrite(10,LOW);
  //      digitalWrite(11,LOW);
  //      delay(50);
        digitalWrite(12,LOW);
        digitalWrite(13,LOW);
    }
    Serial.print("steps: " );
    Serial.print(stepCount);
    Serial.print(" ");
    Serial.println(digitalRead(5));
  }
}

