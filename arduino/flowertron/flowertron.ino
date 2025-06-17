#include <Arduino.h>
#include <BasicEncoder.h>
#include <TimerOne.h>

// bool pressed = false;
// bool zoomed = false;
// bool backpressed = false;

// int prev_encoder_change;

unsigned long timer;
unsigned long interval = 20;

// int prevPin2 = LOW;
// int prevPin3 = LOW;
int prevEncoder = 0;
int prevPin4 = LOW;
int prevPin5 = LOW;
int prevPin6 = LOW;
int prevPin7 = LOW;
int prevPin9 = LOW;
bool zoomed = false;

BasicEncoder encoder(2, 3);

void timerService() {
  encoder.service();
}

void setup() {
  Serial.begin(9600);

  Timer1.initialize(1000);
  Timer1.attachInterrupt(timerService);

  // pinMode(2, INPUT);
  //pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(9, INPUT);

  timer = millis();
}

void loop() {
  if (millis() - timer >= interval) {
    timer = millis();
    int pin4 = digitalRead(4);
    int pin5 = digitalRead(5);
    int pin6 = digitalRead(6);
    int pin7 = digitalRead(7);
    int pin9 = digitalRead(9);

    int encoderChange = encoder.get_change();
    if (encoderChange) {
      if (encoderChange > 0) {
        Serial.println("L");
      } else {
        Serial.println("R");
      }
    }

    if (pin4 != prevPin4 && pin4 == HIGH) {
      Serial.println("B");
    }

    if (pin6 != prevPin6 && pin6 == HIGH) {
      Serial.println("P");
    }

    if (pin5 != prevPin5 && pin5 == HIGH) {
      Serial.println("Z"); 
    }

    if (pin7 != prevPin7 && pin7 == HIGH) {
      Serial.println("O");
    }

    if (pin9 != prevPin9) {
      Serial.println("I");
    }

    prevPin4 = pin4;
    prevPin5 = pin5;
    prevPin6 = pin6;
    prevPin7 = pin7;
    prevPin9 = pin9;
  }
}
