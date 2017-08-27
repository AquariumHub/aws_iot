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
rootCAPath = "./root-CA.crt"
certificatePath = "./7de6077801-certificate.pem.crt"
privateKeyPath = "./7de6077801-private.pem.key"
MY_TOPIC = "sensingData"

myAWSIoTMQTTClient = AWSIoTMQTTClient("publish")
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and publish to AWS IoT
print("connecting")
myAWSIoTMQTTClient.connect()
print("connected")

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient
value = bridgeclient()

# Publish to the same topic in a loop forever
while True:
    brightness = value.get("Brightness")
    temperature = value.get("Temperature")
    print "Bright: " + brightness
    print "Temp: " + temperature
    time.sleep(1)

    t = time.time();
    date = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d%H%M%S')
    print "brightness: %d, temperature: %d" % (float(brightness), float(temperature))
    myAWSIoTMQTTClient.publish("sensingData", json.dumps({"time": date, "temperature": temperature, "brightness": brightness}), 1)

