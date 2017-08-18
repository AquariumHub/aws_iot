import os
import sys
import logging
import time
import getopt
import json
import datetime
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Read in command-line parameters
host = "a2bdrinkbnov3t.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "../AWS/root-CA.crt"
certificatePath = "../AWS/AquariumHub.cert.pem"
privateKeyPath = "../AWS/AquariumHub.private.key"
MY_TOPIC = "sensingData"

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

# Custom MQTT message callback
def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")
  
  data = json.loads(message.payload)
  Press = data['temperature']
  print('temperature: ')
  print Press
  

while True:
  myAWSIoTMQTTClient.subscribe(MY_TOPIC, 0, customCallback)

time.sleep(2)
