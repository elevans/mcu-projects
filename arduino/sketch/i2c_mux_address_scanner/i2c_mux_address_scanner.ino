# include "Wire.h"

# define MUX_ADDRESS 0x70

void muxselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  while (!Serial);
  delay(1000);

  Wire.begin();
  Serial.begin(9600);
  Serial.println("\n I2C Multiplexer scanner ready...");

  for (uint8_t t = 0; t < 8; t++) {
    muxselect(t);
    Serial.print("MUX Port #");
    Serial.println(t);

    for (uint8_t addr = 0; addr <= 127; addr++) {
      if (addr == MUX_ADDRESS) continue;
      Wire.beginTransmission(addr);
      if (!Wire.endTransmission()) {
        Serial.print("Found I2C 0x");
        Serial.println(addr, HEX);
      }
    }
  }
  Serial.println("\nDone.");
}

void loop() {
}
