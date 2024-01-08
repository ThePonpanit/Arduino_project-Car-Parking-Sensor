#include <TridentTD_LineNotify.h>

#define SSID        "Ww"                                     
#define PASSWORD    "12345678"                                   


const int trigPin = D6;
const int echoPin = D5;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(LINE.getVersion());

  WiFi.begin(SSID, PASSWORD);
  Serial.printf("กำลังเชื่อมต่อ WiFi กับ %s\n",  SSID);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(400);
  }
  Serial.printf("\nเชื่อมต่อ WiFi สำเร็จ\nIP : ");
  Serial.println(WiFi.localIP());

  LINE.setToken(LINE_TOKEN);
}

#define UID "sensor_01"  // Unique identifier for this sensor

void loop() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);

  int distance = duration * 0.034 / 2;
  
  // Correct usage of printf with format specifiers
  Serial.printf("ระยะทาง: %d เซนติเมตร\n", distance);

  String message = "UID: " + String(UID) + ", ระยะทาง: " + String(distance) + " เซนติเมตร";
  
  LINE.notify(message);

  delay(5000);
}
