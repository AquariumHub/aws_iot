#include <OneWire.h> 
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <Bridge.h>

// Data wire is plugged into pin 10 on the Arduino 
const int PIN_ONE_WIRE = 10;  // one-wire (DS18B20) 接腳
const int PIN_LIGHT_SENSOR = A0;  // 光敏電阻 (Grove Light Sensor) 接腳

const int CMD_A360 = 0;

// Json string
String str;

// Setup a oneWire instance to communicate with any OneWire devices  
// (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(PIN_ONE_WIRE); 

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

void setup(void) 
{
  Serial.begin(115200);  // 跟電腦連接的 COM
  Serial1.begin(57600);  // 跟 MT7688 MPU 連接的 COM
  sensors.begin();
  Bridge.begin();
}

void loop(void) 
{ 
  // call sensors.requestTemperatures() to issue a global temperature 
  // request to all devices on the bus 
  
  Serial.print("\nRequesting temperatures..."); 
  sensors.requestTemperatures(); // Send the command to get temperature readings 
  Serial.println("DONE"); 
  
  Serial.print("Temperature is: "); 
  float temperatureValue = sensors.getTempCByIndex(0); // Why "byIndex"?
  // You can have more than one DS18B20 on the same bus.
  // 0 refers to the first IC on the wire 
  Serial.println(temperatureValue);

  int brightnessValue = analogRead(PIN_LIGHT_SENSOR);
  Serial.print("Light sensor value = ");
  Serial.println(brightnessValue);

  // MCU to MPU
  Bridge.put("Temperature", String(temperatureValue));
  Bridge.put("Brightness", String(brightnessValue));

  // deal with json commands from the aws or android app
  if(Serial1.available() > 0)
  {
    // Json Buffer, do not reuse or let it global var
    StaticJsonBuffer<200> jsonBuffer;

    //read string from MPU
    str = Serial1.readStringUntil('\n');
    Serial.println(str);

    JsonObject& root = jsonBuffer.parseObject(str);
    if(!root.success())
    {
      Serial.println("parseObject() failed");
      return;
    }
    Serial.println("parseObject() succeed");

    int cmd = root["cmd"];

    if(cmd == CMD_A360)
    {
      int intensity = root["intensity"];
      int color = root["color"];
      Serial.println(String(intensity) + " " + String(color));
      analogWrite(5, (intensity / 100.0) * 255);
      analogWrite(6, (color / 100.0) * 255);
    }
  }
  else
    Serial.println("Serial1 is not available...");
  
  delay(1000);
}
