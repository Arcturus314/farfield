#include <Servo.h>

#define PREBUFFER  100 // ms to wait after moving before sampling
#define POSTBUFFER 100 // ms to wait after sampling before moving

#define SCANBUFFER 2000 // ms to wait between scans
#define NUMANALOGREADSBUFFER 100 // num analog reads to clear things out

#define STARTANGLE 40  // deg angle to start servo scan at
#define STOPANGLE  180 // deg angle to end servo scan at
#define STEPANGLE  1   // deg to step between samples

#define NORMAL 130 // detector arm normal to LED

#define NUMSAMPLES 10  // num photodiode samples to average

#define SERVOPIN 10
#define PHOTODIODEPIN A0

Servo servo;

void setup() {
  Serial.begin(9600);
  servo.attach(SERVOPIN);
}

void loop() {
  // hysteresis compensation
  servo.write(STARTANGLE);
  delay(SCANBUFFER);
  for (int spurioussamples = 0; spurioussamples < NUMANALOGREADSBUFFER; spurioussamples++) analogRead(PHOTODIODEPIN);

  //sampling
  for (int angle = STARTANGLE; angle <= STOPANGLE; angle += STEPANGLE) {
    // moving servo
    servo.write(angle);
    delay(PREBUFFER);

    // sampling
    int samplebuffer = 0;
    for (int samplenum = 0; samplenum < NUMSAMPLES; samplenum++) {
      samplebuffer += analogRead(PHOTODIODEPIN);
    }
    float sampleval = (float) samplebuffer / (float) NUMSAMPLES;
    Serial.print(angle-NORMAL + 90);
    Serial.print(",");
    Serial.println(String(5*sampleval/1023,4));
    
    // waiting
    delay(POSTBUFFER);
  }
}
