#include <SPI.h>
#include <RF24.h>
#include <stdint.h>

const uint8_t address[] = "1PPVP";
RF24 radio(9, 10);

void setup(void) {
  DDRD &= ~0xFC;
  DDRD |= (1<<PIND3) | (1<<PIND5);
  PORTD |= 0xFC;
  PORTD &= ~((1<<PIND3) | (1<<PIND5));
  DDRC &= ~0x3F;
  PORTC |= 0x3F;

  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.openWritingPipe(address);
  radio.stopListening(); 
}

void loop(void) {
  // msg.bit7 must be 0, msg.bit15 must be 1
  static uint16_t prev_msg = 0;
  uint16_t msg = (PIND >> 2) & 0x7F; // D2 - D8
  msg |= (PINC & 0x3F) << 8; // A0 - A5
  msg |= 0x8000;
  if(msg != prev_msg) {
    radio.write(&msg, 2);
    prev_msg = msg;
  }
}
