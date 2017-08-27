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

myAWSIoTMQTTClient = AWSIoTMQTTClient("publish")
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

count = 1
initialValue = 0
while(count <= 10):
	print("count: " + str(count))
	myAWSIoTMQTTClient.publish("$aws/things/AquariumHub/shadow/update", 
	json.dumps(
		{"state" : 
			{"desired" : 
				{"A360" : 
					{"intensity" : initialValue,
					 "color" : initialValue}}}}
	), 1)
	initialValue  = initialValue + 10
	count = count + 1
	time.sleep(3)
	
myAWSIoTMQTTClient.disconnect()