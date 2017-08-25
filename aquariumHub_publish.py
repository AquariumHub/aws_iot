import os
import sys
import time
import json
import datetime
import AWSIoTPythonSDK
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import socket
from pprint import pprint

# Read in command-line parameters
host = "a2bdrinkbnov3t.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "./aws_certifications/root-CA.crt"
certificatePath = "./aws_certifications/7de6077801-certificate.pem.crt"
privateKeyPath = "./aws_certifications/7de6077801-private.pem.key"

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
print('Connecting AWS MQTT broker...')
myAWSIoTMQTTClient.connect()
print('Connected')

"""
def lineNo():
  #Returns the current line number in our program.
  return inspect.currentframe().f_back.f_lineno
"""

# import bridgeclient
# please enable Bridge library on LinkIt Smart 7688 Duo 
'''
    ~# uci set yunbridge.config.disabled='0'
    ~# uci commit
    ~# reboot
'''
sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient
value = bridgeclient()

TOPIC_SENSING_DATA = "sensingData"

while True:
    brightness = value.get("Brightness")
    temperature = value.get("Temperature")
    print "Bright: " + brightness
    print "Temp: " + temperature
    time.sleep(1)
    
    timeObject = time.time();
    date = datetime.datetime.fromtimestamp(timeObject).strftime('%Y%m%d%H%M%S')
    print "brightness: %d, temperature: %d" % (float(brightness), float(temperature))
    myAWSIoTMQTTClient.publish("TOPIC_SENSING_DATA", json.dumps({"time": date, "temperature": temperature, "brightness": brightness}), 1)
    
myAWSIoTMQTTClient.disconnect()
