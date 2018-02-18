#include <SPI.h>
#include <RF24.h>
#include <stdint.h>

#define BAUD  115200
#define MSG_SIZE  2
#define BUTTON_INVALID 0x8000
#define NUM_USERS  2

const uint8_t addresses[][6] = {"1PPVP","2PPVP"};
RF24 radio(9, 10);

void setup(void) {
  Serial.begin(BAUD);
  Serial.println("Hello!");
  
  radio.begin();
  for(uint8_t i = 1; i < NUM_USERS + 1; ++i) {
    radio.openReadingPipe(i, addresses[i - 1]);
  }
  radio.startListening();
}

void loop(void)
{
  uint8_t pipe_num, msg_bytes[] = {0, 0};
  uint16_t buttons[] = {BUTTON_INVALID, BUTTON_INVALID};
  if(radio.available(&pipe_num)) {
    if((pipe_num > 0) && (pipe_num < NUM_USERS + 1)) {
      radio.read(msg_bytes, MSG_SIZE);
      if(!(msg_bytes[1] & 0x80)) {
        //Serial.print("Wrong message on pipe ");
        //Serial.println(pipe_num, DEC);
      } else {
        buttons[pipe_num - 1] = msg_bytes[0] | (msg_bytes[1] & ~0x80) << 6;
        buttons[pipe_num - 1] ^= 0xFFFF;
      }
    }
  }
  for(uint8_t i = 0; i < NUM_USERS; ++i) {
    if(buttons[i] != BUTTON_INVALID) {
      //Serial.write(i)
      Serial.write((uint8_t*)(&buttons[i]), 2);
    }
  }
}
