import os
import sys
import logging
import time
import getopt
import json
import datetime
import AWSIoTPythonSDK
import serial
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Read in command-line parameters
host = "a2bdrinkbnov3t.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "../AWS/root-CA.crt"
certificatePath = "../AWS/AquariumHub.cert.pem"
privateKeyPath = "../AWS/AquariumHub.private.key"
MY_TOPIC = "$aws/things/AquariumHub/shadow/update"

myAWSIoTMQTTClient = AWSIoTMQTTClient("subscribe")
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

CMD_A360 = 1;

# Custom MQTT message callback
def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")
  
  data = json.loads(message.payload)
  intensity_a360 = data['state']['desired']['A360']['intensity']
  print('intensity: ')
  print intensity_a360
  color_a360 = data['state']['desired']['A360']['color']
  print('color: ')
  print color_a360
  
  myport = serial.Serial("/dev/ttyS0", 57600, timeout= 0.5 )
  jsonObject = json.dumps({"cmd":CMD_A360, "intensity":intensity_a360, "color":color_a360})
  myport.write(jsonObject)
  myport.close()
  
def cmd_ap700(intensity_ap700, color_ap700):
  
  
while True:
  myAWSIoTMQTTClient.subscribe(MY_TOPIC, 0, customCallback)

time.sleep(2)
