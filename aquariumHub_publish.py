import os
import serial
import sys
import time
import json
import datetime
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import socket
from exception_handler import GracefulKiller

# Read in command-line parameters
host = "a2bdrinkbnov3t.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "./aws_certifications/root-CA.crt"
certificatePath = "./aws_certifications/7de6077801-certificate.pem.crt"
privateKeyPath = "./aws_certifications/7de6077801-private.pem.key"

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
print('Connecting AWS MQTT broker...')
myAWSIoTMQTTClient.connect()
print('Connected')

"""
def lineNo():
  #Returns the current line number in our program.
  return inspect.currentframe().f_back.f_lineno
"""

# import bridgeclient
# if you want to use bridge instead
# please enable Bridge library on LinkIt Smart 7688 Duo 
'''
uci set yunbridge.config.disabled='0'
uci commit
reboot

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient
value = bridgeclient()
'''

TOPIC_SENSING_DATA = "sensingData"

ser = serial.Serial("/dev/ttyS0", 57600)

killer = GracefulKiller()
while True:
  if killer.kill_now:
    break
  try:
    data = json.loads(ser.readline())
    brightness = data['Brightness']
    temperature = data['Temperature']
    lightFrequency = data['LightFrequency']
    #pH = data['pH']
  except Exception as e:
    print "Errors occurred while getting sensing data from serial port. "
    print "The exception is " + str(e)
    pass
  timeObject = time.time();
  date = datetime.datetime.fromtimestamp(timeObject).strftime('%Y%m%d%H%M%S')
  print "\ndate: " + datetime.datetime.fromtimestamp(timeObject).strftime('%Y/%m/%d %H:%M:%S')
  print "Brightness: " + str(brightness)
  print "Temperature: " + str(temperature)
  print "Light Frequency: " + str(lightFrequency) + "\n"
  #print "pH: " + pH
  print "------------------------------------"
  try:
    myAWSIoTMQTTClient.publish(TOPIC_SENSING_DATA, json.dumps({"time": date, "temperature": temperature, "brightness": brightness, "lightFrequency": lightFrequency}), 1)
  except Exception as e:
    print str(e)
    pass
  time.sleep(2)
print "Stopped"
myAWSIoTMQTTClient.disconnect()
