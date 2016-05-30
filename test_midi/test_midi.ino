int noOfPads = 2;
int pin = 0;     
int forceReading = 0;

void setup() 
{
  //Serial.begin(115200);                                  // connect to the serial port 115200
  Serial.begin(10);  
}


void loop() {
  for(int pin=0; pin < noOfPads; pin++){
    delay(100);
    forceReading = analogRead(pin);                              // read the input pin
    int ledPin = pin + 9;
    analogWrite(ledPin, forceReading/4);
    
    Serial.print(forceReading);

    if(pin < noOfPads-1){    
      Serial.print("\t");  
    } else {
      Serial.println();
    }
  } 
}

