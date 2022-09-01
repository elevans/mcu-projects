int ledPin = 3;    // LED connected to digital pin 3
int ledWriteValue = 0;
int potPin = A0; 
int potReadValue = 0;


void setup()  
    { 
     pinMode(ledPin, OUTPUT);
    } 
 
void loop() 
    { 
     potReadValue = analogRead(A0);
     ledWriteValue = map(potReadValue, 0, 1024, 0, 255);
     analogWrite(ledPin, ledWriteValue);                 
    }
