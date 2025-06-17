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
int prevPin6 = LOW;
int prevPin9 = LOW;
int prevPin10 = LOW;
int prevPin11 = LOW;
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
  pinMode(6, INPUT);
  pinMode(9, INPUT);
  pinMode(10, INPUT);
  pinMode(11, INPUT);

  timer = millis();
}

void loop() {
  if (millis() - timer >= interval) {
    timer = millis();
    int pin4 = digitalRead(4);
    int pin6 = digitalRead(6);
    int pin9 = digitalRead(9);
    int pin10 = digitalRead(10);
    int pin11 = digitalRead(11);

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

    if (pin9 != prevPin9) {
      Serial.println("I");
    }
    
    if (pin10 != prevPin10 && pin10 == HIGH) {
      Serial.println("O");
    }
    
    if (pin11 != prevPin11 && pin11 == HIGH) {
      Serial.println("Z"); 
    }
    

    prevPin4 = pin4;
    prevPin11 = pin11;
    prevPin6 = pin6;
    prevPin10 = pin10;
    prevPin9 = pin9;
  }
}
