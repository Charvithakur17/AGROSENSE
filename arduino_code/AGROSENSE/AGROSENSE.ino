#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Pins
int soilPin = 32;
int ldrPin = 34;

// Variables
int moisture;
int ldrValue;
float temperature;
float humidity;
String status;

// WiFi
const char* ssid = "YOUR PASSWORD NAME";
const char* password = "YOUR PASSWORD";
const char* serverName = "http://your_ip:5000//data";

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.println(WiFi.localIP());
}

void loop() {

  // Read sensors
  moisture = analogRead(soilPin);
  ldrValue = analogRead(ldrPin);
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Soil logic
  if (moisture > 3500) status = "DRY";
  else if (moisture > 2900) status = "NORMAL";
  else status = "WET";

  Serial.println("------ SENSOR DATA ------");
  Serial.print("Moisture: "); Serial.println(moisture);
  Serial.print("Status: "); Serial.println(status);
  Serial.print("Temp: "); Serial.println(temperature);
  Serial.print("Humidity: "); Serial.println(humidity);
  Serial.print("Light: "); Serial.println(ldrValue);

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"moisture\":" + String(moisture) + ",";
    json += "\"status\":\"" + status + "\",";
    json += "\"temperature\":" + String(temperature) + ",";
    json += "\"humidity\":" + String(humidity) + ",";
    json += "\"ldr\":" + String(ldrValue);
    json += "}";

    int response = http.POST(json);

    Serial.print("Server Response: ");
    Serial.println(response);

    http.end();
  }

  delay(5000);
}