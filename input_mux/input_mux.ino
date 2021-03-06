int noOfPads = 2;
int pin = 0;     
int forceReading = 0;


//Mux control pins
int en = 12;          //blue
int s0 = 11;          //orange
int s1 = 10;          //yellow
int s2 = 9;           //green
int s3 = 8;           //purple

//Mux in "SIG" pin
int SIG_pin = 0;      //grey


void setup(){
  pinMode(en, OUTPUT);
  pinMode(s0, OUTPUT); 
  pinMode(s1, OUTPUT); 
  pinMode(s2, OUTPUT); 
  pinMode(s3, OUTPUT); 

  digitalWrite(en, LOW);
  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);

  Serial.begin(60);
  //Serial.begin(9600);
}


void loop(){

  //Loop through and read all 16 values
  for(int i = 0; i < 12; i ++){
    delay(10);

    forceReading = readMux(i);                              // read the input pin
    //int ledPin = pin + 9;
    //analogWrite(ledPin, forceReading/4);
    
    Serial.print(forceReading);

    if(i < 11){    
      Serial.print("\t");  
    } 
    else{
      Serial.println();
    }

  }

}


int readMux(int channel){
  int controlPin[] = {s0, s1, s2, s3};

  int muxChannel[16][4]={
    {0,0,0,0}, //channel 0
    {1,0,0,0}, //channel 1
    {0,1,0,0}, //channel 2
    {1,1,0,0}, //channel 3
    {0,0,1,0}, //channel 4
    {1,0,1,0}, //channel 5
    {0,1,1,0}, //channel 6
    {1,1,1,0}, //channel 7
    {0,0,0,1}, //channel 8
    {1,0,0,1}, //channel 9
    {0,1,0,1}, //channel 10
    {1,1,0,1}, //channel 11
    {0,0,1,1}, //channel 12
    {1,0,1,1}, //channel 13
    {0,1,1,1}, //channel 14
    {1,1,1,1}  //channel 15
  };

  //loop through the 4 sig
  for(int i = 0; i < 4; i ++){
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }

  //read the value at the SIG pin
  int val = analogRead(SIG_pin);

  //return the value
  return val;
}


