#include <Servo.h>
#include <AccelStepper.h>

const int maxAcceleration = 100;  // steps per second per second
const int penDownServoPosition = 90;
const int penUpServoPosition = 60;
const int zOn = 1;  // z below 1 will drop pen

AccelStepper stepperA(1,9,8);  
AccelStepper stepperB(1,7,6);  
Servo penServo;
int servoPos = 0;

void setup() {  
  // start serial port at 115200 bps:
  Serial.begin(115200);
  establishContact();  // send a byte to establish contact until receiver responds   
  
  // set "max" acceleration
  stepperA.setAcceleration(1000);
  stepperB.setAcceleration(1000);
  stepperA.setMaxSpeed(10000);
  stepperB.setMaxSpeed(10000);
  
  // initialize servo
  penServo.attach(3);
  penUp();
}

char getByte() {
  while (Serial.available() <= 0) {}
  return Serial.read();
}

int getInput() {
  char inByte;
  String input = "";
  inByte = getByte();
  while(inByte != ';') {
    input.concat(inByte);
    inByte = getByte();
  }
  return input.toInt();
}

void penDown() {
  // lower pen
  if(servoPos != penDownServoPosition) {
    penServo.write(penDownServoPosition);
    servoPos = penDownServoPosition;
    delay(200);
  }
}

void penUp() {
  // raise pen
  if(servoPos != penUpServoPosition) {
    penServo.write(penUpServoPosition);
    servoPos = penUpServoPosition;
    delay(200);
  }
}

void move(int dA, int dB, int maxSpeed) {
  int aSteps = abs(dA), bSteps = abs(dB);
  float aSpeed = aSteps >= bSteps ? maxSpeed : (float) aSteps / ((float) bSteps / maxSpeed);
  float bSpeed = bSteps >= aSteps ? maxSpeed : (float) bSteps / ((float) aSteps / maxSpeed); 
  stepperA.move(dA);
  stepperB.move(dB);
  stepperA.setSpeed(aSpeed);
  stepperB.setSpeed(bSpeed);
  while(stepperA.distanceToGo() != 0 || stepperB.distanceToGo() != 0) {
    stepperA.runSpeedToPosition();
    stepperB.runSpeedToPosition();
  }
}

void loop()
{
  float x, y, z, f;
  if (Serial.available() > 0) {
    x = getInput();
    y = getInput();
    z = getInput();
    f = getInput();
    if(z >= zOn) {
      penUp();
    } 
    else {
      penDown();
    } 
    move(x, y, f);
    Serial.println('done');
  }
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}
