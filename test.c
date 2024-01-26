#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>

 
#define SSID        "Yui_2.4G"                                     
#define PASSWORD    "04122518"
#define TEST_API_ENDPOINT "http://httpbin.org/post"  // Updated API endpoint for testing
#define API_ENDPOINT "https://parkinglot-api-409510.et.r.appspot.com/receive_data"  // Updated API endpoint for testing
#define UID "sensor_01"
 
const int trigPin = D6;
const int echoPin = D5;
boolean isSpotFree = true;

void testApiConnection() {
    WiFiClientSecure client;
    HTTPClient http;

    Serial.println("Testing API connection...");

    client.setInsecure(); // Use this for testing purposes only, as it skips SSL verification
    http.begin(client, "https://parkinglot-api-409510.et.r.appspot.com/"); // Your API endpoint

    int httpCode = http.GET();

    if (httpCode > 0) {
        String payload = http.getString();
        Serial.println("Received response from API:");
        Serial.println(payload);
    } else {
        Serial.print("Error on API GET: ");
        Serial.println(http.errorToString(httpCode));
    }

    http.end();
}

 
void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASSWORD);
  Serial.printf("Connecting to WiFi %s\n",  SSID);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
  }
  Serial.printf("\nConnected to WiFi\nIP: ");
  Serial.println(WiFi.localIP());
 
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  testApiConnection();
}
 
void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
 
  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;
 
  Serial.printf("Distance: %d cm\n", distance);
 
  boolean currentStatus = (distance > 200); // Spot is free if nothing is within 2 meters
 
  if (currentStatus != isSpotFree) {
    isSpotFree = currentStatus;
 
    if (testConnection()) {
      sendToAPI(UID, distance);
    } else {
      Serial.println("Network test failed, not sending data to API");
    }
  }
 
  delay(5000);
}
 
bool testConnection() {
  WiFiClient client;
  HTTPClient http;
 
  Serial.println("Performing network test...");
  http.begin(client, "http://httpbin.org/get");
  int httpCode = http.GET();
 
  if (httpCode > 0) {
    Serial.println("Network test successful");
    http.end();
    return true;
  } else {
    Serial.print("Network test failed: ");
    Serial.println(http.errorToString(httpCode));
    http.end();
    return false;
  }
}
 
void sendToAPI(const char* uid, int distance) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // Bypass SSL certificate verification
    HTTPClient http;
 
    http.begin(client, API_ENDPOINT); // Use the test API endpoint
    http.addHeader("Content-Type", "application/json");
 
    StaticJsonDocument<200> doc;
    JsonArray array = doc.to<JsonArray>();
    JsonObject obj = array.createNestedObject();
    obj["uid"] = uid;
    obj["distance"] = distance;
 
    String output;
    serializeJson(array, output);
 
    Serial.println("JSON being sent: ");
    Serial.println(output);
 
    int httpResponseCode = http.POST(output);
 
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("API Response: " + response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
      Serial.println(http.errorToString(httpResponseCode));
    }
    http.end();
  }
}
