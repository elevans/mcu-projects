#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "ClosedCube_HDC1080.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET 4
#define SCREEN_ADDRESS 0x3C
#define MUX_ADDRESS 0x70
#define HDC1080_ADDRESS 0x40

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
ClosedCube_HDC1080 hdc1080_i;
ClosedCube_HDC1080 hdc1080_o;

const uint8_t sensorButtonPin = 2;
const uint8_t unitButtonPin = 3;

uint8_t sensorButtonState = 0;
uint8_t lastSensorButtonState = 0;
uint8_t sensorSelect = 1;
uint8_t unitButtonState = 0;
uint8_t lastUnitButtonState = 0;
uint8_t unitSelect = 0;
double temp = 0;
double hum = 0;
double f_temp = 1;
unsigned long currentMillis = 0;
unsigned long lastInsideSensorMillis = 0;
unsigned long lastOutsideSensorMillis = 0;
unsigned long lastSensorButtonStateMillis = 0;

void muxselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(1 << i);
  Wire.endTransmission();
}

double getTemp(ClosedCube_HDC1080 sensor, uint8_t bus) {
  muxselect(bus);
  return sensor.readTemperature();
}

double getHum(ClosedCube_HDC1080 sensor, uint8_t bus) {
  muxselect(bus);
  return sensor.readHumidity();
}

void displayTempHum(uint8_t bus, uint8_t sensor, uint8_t temp_unit) {
  // get temp (c) and hum (%)
  if (sensor == 1) {
    temp = getTemp(hdc1080_i, 1);
    hum = getHum(hdc1080_i, 1);
  } else {
    temp = getTemp(hdc1080_o, 2);
    hum = getHum(hdc1080_o, 2);
  }

  // switch bus and display data
  muxselect(bus);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);

  if (sensor == 1) {
    display.print(F("Ti: "));
  } else {
    display.print(F("To: "));
  }
  if (temp_unit == 1) {
    display.print(temp, 1);
    display.print(F("C\n"));
  } else {
    f_temp = (temp * 1.8) + 32;
    display.print(f_temp, 1);
    display.print(F("F\n"));
  } 

  if (sensor == 1) {
    display.print(F("Hi: "));
  } else {
    display.print(F("Ho: "));
  }

  display.print(hum, 1);
  display.print(F("%"));
  display.display();
}

void setup() {
  // initialize serial communication
  Serial.begin(9600);

  // setup sensor button
  pinMode(sensorButtonPin, INPUT);
  pinMode(unitButtonPin, INPUT);

  // setup inside temp/hum sensor
  muxselect(1);
  hdc1080_i.begin(HDC1080_ADDRESS);

  // setup outside temp/hum sensor
  muxselect(2);
  hdc1080_o.begin(HDC1080_ADDRESS);

  // Initialize OLED on MUX port 0
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  muxselect(0);
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // initialize the screen
  display.display();
  delay(3000);
  }

void loop() {
  // sense sensor state change
  sensorButtonState = digitalRead(sensorButtonPin);
  if (sensorButtonState != lastSensorButtonState) {
    if (sensorButtonState == 1) {
      if (sensorSelect == 1) {
        sensorSelect = 2;
      } else {
        sensorSelect = 1;
      }
    }
    lastSensorButtonState = sensorButtonState;
  }

  // sense unit change
  unitButtonState = digitalRead(unitButtonPin);
  if (unitButtonState != lastUnitButtonState) {
    if (unitButtonState == 1) {
      if (unitSelect == 1) {
        unitSelect = 2;
      } else {
        unitSelect = 1;
      }
    }
    lastUnitButtonState = unitButtonState;
  }  
  displayTempHum(0, sensorSelect, unitSelect);
  delay(50);
}
