#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);             // CE, CSN
const byte address[6] = "CAR01";

String inputLine = "";

void setup() {
  Serial.begin(115200);

  if (!radio.begin()) {
    Serial.println("RF24 radio not responding");
    while (1) {}
  }

  radio.setPALevel(RF24_PA_LOW);   // start with LOW for bench testing
  radio.setDataRate(RF24_1MBPS);
  radio.setRetries(5, 15);
  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("Uno RF transmitter ready.");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      inputLine.trim();

      if (inputLine.length() > 0) {
        char payload[32] = {0};
        inputLine.toCharArray(payload, sizeof(payload));

        bool ok = radio.write(&payload, sizeof(payload));

        Serial.print("TX: ");
        Serial.print(inputLine);
        Serial.print(" | RF write = ");
        Serial.println(ok ? "OK" : "FAIL");
      }

      inputLine = "";
    } else {
      inputLine += c;
    }
  }
}
