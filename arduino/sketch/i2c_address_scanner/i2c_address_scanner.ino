#include <Wire.h>

void setup() {
  Wire.begin();

  Serial.begin(9600);
  while(!Serial); //Wait command for arduino leonardo
  Serial.println("\nI2C Scanner");

}

void loop() {
  byte error, address;
  int nDevices;

  Serial.println("Scanning...");
  nDevices = 0;

  for (address = 1; address < 127; address++)
  {
    // ping addresses from 1 to 127 and capture reply
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address < 16)
        Serial.print("0");
      Serial.print(address, HEX);
      Serial.println(" !");
      nDevices++;
    }
    else if (error == 4)
    {
      Serial.print("Unknown error at address 0x");
      if (address < 16)
        Serial.print("0");
      Serial.print(address, HEX);
    }
  }

  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else
    Serial.println("done\n");

  delay(5000); // wait 5 seconds for next scan
}
