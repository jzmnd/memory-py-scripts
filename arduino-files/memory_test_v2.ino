/*
Memory testing sketch
memory_test_v2.ino
Use with memory_test_v1.py
Jeremy Smith
EECS, University of California, Berkeley
Version 2.2
*/

#include <eRCaGuy_Timer2_Counter.h>
#include <Memoryfunctions.h>

#define FASTADC 1
// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

const int ledPin = 13;      // LED pin number
unsigned int inByte;        // incoming serial byte for program number
unsigned int inBuffer[6];   // serial buffer for other data parsed from python
int state;                  // read state (1 or 0)


/*
Setup function
  Blinks LED
  Sets ADC smple rate
  Initializes pins and sets initial voltages
  Sends establish contact byte 'A'
*/

void setup(){
  pinMode(ledPin, OUTPUT);
  for (int i=0; i<4; i++){            // blinks LED 4 times before initilization
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
  }
  Serial.begin(115200);
  timer2.setup();             // setup for timer2 counter
  #if FASTADC
    // set prescale to 16 i.e. 1 MHz ADC clock and theoretical 76.9 kHz sample rate (1 Mhz / 13)
    sbi(ADCSRA,ADPS2);
    cbi(ADCSRA,ADPS1);
    cbi(ADCSRA,ADPS0);
  #endif
  delay(1000);
  mem.initPinMode();          // initialization required pin modes to OUTPUT
  mem.initContentAddress();   // initial initialization (all float ready for probing)
  mem.establishContact('A');  // establish contact
}


/*
Main function
   Reads in serial port data from python script
   Runs required function
   Sends establish contact byte 'Z'
*/

void loop(){
  if(Serial.available() >= 7){      // checks if all data is on the serial port
    inByte = Serial.read();         // reads serial data from python
    for (int i=0; i<6; i++){
      inBuffer[i] = Serial.read();  // reads serial data from python into buffer
    }

    if(inByte == '1'){
      // Content addressable read
      digitalWrite(ledPin, HIGH);
      mem.initContentAddress();                       // reinitialize
      for (int i=0; i<inBuffer[5]; i++){
        mem.precharge(inBuffer[4], inBuffer[0]);      // precharge time, WL number
      }
      mem.applypattern(inBuffer[2], inBuffer[3]);     // pattern (binary), time for applying pattern in ms
      mem.wordlineread(inBuffer[0]);                  // WL number
      mem.gndall(100);                                // grounds all lines for 100 ms
      digitalWrite(ledPin, LOW);
    }

    if(inByte == '2'){
      // Form all bits
      digitalWrite(ledPin, HIGH);
      mem.initOneThirdTwoThirdZERO();       // 1/3-2/3 initialize ZERO write
      for (int i=0; i<inBuffer[5]; i++){
        mem.forming(inBuffer[4]);           // forming time in ms (set all bits to 0-state)
      }
      mem.gndall(100);                      // grounds all lines for 100 ms
      digitalWrite(ledPin, LOW);
    }

    if(inByte == '3'){
      // Write a ZERO state
      digitalWrite(ledPin, HIGH);
      mem.initOneThirdTwoThirdZERO();       // 1/3-2/3 initialize ZERO write
      for (int i=0; i<inBuffer[5]; i++){
        mem.stdwriteZERO(inBuffer[0], inBuffer[1], inBuffer[3]);       // write 0 to bit w, b, for time in ms
      }
      mem.gndall(100);                      // grounds all lines for 100 ms
      digitalWrite(ledPin, LOW);
    }

    if(inByte == '4'){
      // Write a ONE state
      digitalWrite(ledPin, HIGH);
      mem.initOneThirdTwoThirdONE();       // 1/3-2/3 initialize ONE write
      for (int i=0; i<inBuffer[5]; i++){
        mem.stdwriteONE(inBuffer[0], inBuffer[1], inBuffer[3]);        // write 1 to bit w, b, for time in ms
      }
      mem.gndall(100);                      // grounds all lines for 100 ms
      digitalWrite(ledPin, LOW);
    }

    if(inByte == '5'){
      // Standard read
      digitalWrite(ledPin, HIGH);
      mem.initOneThirdTwoThirdZERO();       // 1/3-2/3 initialize ZERO write
      state = mem.stdread(inBuffer[0], inBuffer[1], inBuffer[3]);           // read at bit w, b, for time in ms
      Serial.println(state);
      if (state == 1){                                                      // rewrite bit if it was a 1 state
        mem.initOneThirdTwoThirdONE();
        for (int i=0; i<inBuffer[5]; i++){
          mem.stdwriteONE(inBuffer[0], inBuffer[1], inBuffer[3]);           // write 1 to bit w, b, for time in ms
        }
        mem.gndall(100);                      // grounds all lines for 100 ms
      }
      digitalWrite(ledPin, LOW);
    }

    delay(1000);
    mem.establishContact('Z');
  }
}
