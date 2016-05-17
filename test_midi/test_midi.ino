int noOfPads = 2;

unsigned char PadNote[6] = {60,62,64,67,69,72};         // MIDI notes from 0 to 127 (Mid C = 60)

int PadCutOff[6] = {50,50,50,50,50,50};           // Minimum Analog value to cause a drum hit

int MaxPlayTime[6] = {90,90,90,90,90,90};               // Cycles before a 2nd hit is allowed

#define  midichannel  0;                              // MIDI channel from 0 to 15 (+1 in "real world")

boolean VelocityFlag  = true;                           // Velocity ON (true) or OFF (false)

unsigned long curSec;
unsigned long previousSec;




//*******************************************************************************************************************
// Internal Use Variables     
//*******************************************************************************************************************

boolean activePad[6] = {0,0,0,0,0,0};                   // Array of flags of pad currently playing
int PinPlayTime[6] = {0,0,0,0,0,0};                     // Counter since pad started to play

unsigned char status;

int pin = 0;     
int forceReading = 0;
int velocity = 0;

//*******************************************************************************************************************
// Setup      
//*******************************************************************************************************************

void setup() 
{
  Serial.begin(115200);                                  // connect to the serial port 115200
  //Serial.begin(9600);
  
  //delay(1000);
}

//*******************************************************************************************************************
// Main Program     
//*******************************************************************************************************************

void loop() {

  //curSec = millis();
  
  for(int pin=0; pin < noOfPads; pin++){

    //delay(100);
    forceReading = analogRead(pin);                              // read the input pin
    int ledPin = pin + 9;
    analogWrite(ledPin, forceReading/4);
    
    // plot graph testing
    Serial.print(forceReading);

    if(pin < noOfPads-1){
      Serial.print("\t");  
    } else {
      Serial.println();
    }
    
    velocity = map(forceReading, 0, 1023, 0, 127);

    if(forceReading > PadCutOff[pin]){ 
      
      if((activePad[pin] == false)){

        delay(50);
        //forceReading = analogRead(pin);
        //velocity = map(forceReading, 0, 1023, 0, 127);

        //MIDI_TX(144,PadNote[pin],velocity); 
        PinPlayTime[pin] = 0;
        activePad[pin] = true;
      }
      else
      {
        PinPlayTime[pin] = PinPlayTime[pin] + 1;
      }
    }
    else if((activePad[pin] == true))
    {
      PinPlayTime[pin] = PinPlayTime[pin] + 1;
      //MIDI_TX(144,PadNote[pin],velocity);
      
      if(PinPlayTime[pin] > MaxPlayTime[pin])
      {
        activePad[pin] = false;
        //MIDI_TX(128,PadNote[pin],127); 
      }
    }
  } 
}


// Transmit MIDI Message      
/*void MIDI_TX(unsigned char MESSAGE, unsigned char PITCH, unsigned char VELOCITY) 
{
  status = MESSAGE + midichannel;
  Serial.write(status);
  Serial.write(PITCH);
  Serial.write(VELOCITY);
}
*/
