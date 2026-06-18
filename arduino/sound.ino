int soundSensorPin = A0;  // analog pin
int soundValue = 0;

void setup() {
  Serial.begin(9600);  // start serial communication
}

void loop() {
  soundValue = analogRead(soundSensorPin);  // read sensor
  Serial.println(soundValue);               // send to PC
  delay(200);  // wait a bit before next reading
}