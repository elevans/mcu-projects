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
const uint8_t unitButtonPin = 4;

uint8_t sensorButtonState = 0;
uint8_t lastSensorButtonState = 0;
uint8_t sensorSelect = 1;
uint8_t unitButtonState = 0;
uint8_t lastUnitButtonState = 0;
uint8_t unitSelect = 0;
uint8_t sensorCnt = 0;
uint8_t unitCnt = 0;
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
  // read button state
  sensorButtonState = digitalRead(sensorButtonPin);
  unitButtonState = digitalRead(unitButtonPin);
  
  // iterate sensorCnt and output the other sensor data
  if (sensorButtonState == 1) {
    sensorCnt = sensorCnt + 1;
    if (sensorCnt == 1) {
      sensorSelect = 2;
    } else {
      sensorSelect = 1;
      sensorCnt = 0;
    }
  }
  // sense unit change
  if (unitButtonState == 1) {
    unitCnt = unitCnt + 1;
    if (unitCnt == 1) {
      unitSelect = 2;
    } else {
      unitSelect = 1;
      unitCnt = 0;
    }
  }

  displayTempHum(0, sensorSelect, unitSelect);
  
  //50 was really fast... 500 is still updating 2x per second. 
  //You'll have to test this delay a bit as you don't want to compete with your button push speed :)
  delay(500);
}
