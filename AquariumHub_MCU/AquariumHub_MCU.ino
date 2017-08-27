#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <Bridge.h>

// Data wire is plugged into pin 10 on the Arduino
const int PIN_ONE_WIRE = 10;  // one-wire (DS18B20) 接腳
const int PIN_LIGHT_SENSOR = A0;  // 光敏電阻 (Grove Light Sensor) 接腳

volatile unsigned long count = 0;
unsigned long oldcount = 0;
unsigned long t = 0;
unsigned long last;

const int CMD_A360 = 1;

// Json string
String str;

// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(PIN_ONE_WIRE);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

void irq()
{
  count++;
}

void setup(void)
{
  Serial.begin(115200);  // 跟電腦連接的 COM
  Serial1.begin(57600);  // 跟 MT7688 MPU 連接的 COM
  sensors.begin();
  pinMode(7, INPUT);  // light frequency
  digitalWrite(7, HIGH);
  attachInterrupt(4, irq, RISING);
  //Bridge.begin();
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
  Serial.print("Brightness sensor_1 value = ");
  Serial.println(brightnessValue);

  int val;
  val=analogRead(0);   //connect grayscale sensor to Analog 0
  Serial.print("Brightness sensor_2 value: ");
  Serial.println(val,DEC);//print the value to serial

  if (millis() - last >= 1000)
  {
    unsigned long denominator = millis() - last;
    last = millis();
    t = count;
    unsigned long lightFrequencyValue = (t - oldcount) * 1000 / denominator;
    Serial.print("Frequency: "); 
    Serial.print(lightFrequencyValue);
    Serial.print("\t = "); 
    Serial.print((lightFrequencyValue+50)/100);  // +50 == rounding last digit
    Serial.println(" mW/m2");
    oldcount = t;

    // MCU to MPU
    Bridge.put("LightFrequency", String(lightFrequencyValue));
  }

  // MCU to MPU
  Bridge.put("Temperature", String(temperatureValue));
  Bridge.put("Brightness", String(brightnessValue));

  // deal with json commands from the aws or android app
  if (Serial1.available() > 0)
  {
    // Json Buffer, do not reuse or let it global var
    StaticJsonBuffer<200> jsonBuffer;

    //read string from MPU
    str = Serial1.readStringUntil('\n');
    Serial.println(str);

    JsonObject& root = jsonBuffer.parseObject(str);
    if (!root.success())
    {
      Serial.println("parseObject() failed");
      return;
    }
    Serial.println("parseObject() succeed");

    int cmd = root["cmd"];

    if (cmd == CMD_A360)
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

  delay(500);
}

