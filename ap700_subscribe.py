import os
import sys
import logging
import time
import getopt
import json
import datetime
import AWSIoTPythonSDK
import serial
import subprocess
import inspect
from socket import socket
from pprint import pprint

CMD_A360 = 1;
PORT_AP700 = 8899 # port of ap700
ip_ap700 = [] # list for ip of ap700

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
print('Connecting AWS MQTT broker...')
myAWSIoTMQTTClient.connect()
print('Connected')

def lineNo():
  #Returns the current line number in our program.
  return inspect.currentframe().f_back.f_lineno

#stdout is the stdout of the system call
#return True/False if ap700 is/isn't found
def findap700(stdout):
  iffound_ap700 = False
  
  for line in stdout.readlines():
	temp = line.split(" ")
	if(len(temp) == 5):
	  #if app700 is in the list of dhcp lease
	  if(temp[1]!='undefined' and temp[1].find('ac:cf:23')>-1):
		print('ap700 is found')
		ip_ap700.append(temp[2]) #Add an ip of an ap700 to the end of the list "ip_ap700"
		iffound_ap700 = True
		
  if(iffound_ap700 == False):
    print('ap700 is not found')

  return iffound_ap700
  
def merge_checksum(data, checksum):
  result = []
  result.append(0xA9)
  result = result + data
  result.append(checksum)
  result.append(0x5C)
  
  return result
  
def generate_checksum(data):
  sum = 0
  for i in range(0, len(data), 1):
    sum = sum + data[i]
  return (0x100 - sum) & 0xFF

def merge_length(data):
  result = []
  result.append(len(data)+1)
  result = result + data
  
  return result
  
def genCmd(data):
  #produce data length and merge into data list
  data = merge_length(data)
  
  #generate checksum
  checksum = generate_checksum(data)
  
  #merge checksum and into data list and produce the final cmd for ap700
  data = merge_checksum(data, checksum)
  
  
  return data
  
def sendCmd_AP700(ap700cmd, ip_ap700):
  client = socket(socket.AF_INET,socket.SOCK_STREAM) # define socket type TCP
  client.connect((ip_ap700, PORT_AP700))
  client.sendall(bytes(ap700cmd))
  client.close()

def cmd_ap700(intensity_ap700, color_ap700):
  #system call for the list of dhcp lease
  SYSCMD = 'cat /tmp/dhcp.leases'
  print(SYSCMD)
  process = subprocess.Popen(SYSCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  
  #find ap700 ip and store it into global list 'ip_ap700'
  findap700(process.stdout)
  returnValue = process.wait()
  
  data = [0x01, 0x00 , 0x10 , intensity_ap700, color_ap700]
  
  """if(intensity_ap700 == 0):
	data = [01,00,01,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,00,00,00,00,00,0]
  """
  #generate command for ap700 to set light intensity and color
  ap700cmd = genCmd(data)
  
  for i in range(0, len(ip_ap700), 1):
	sendCmd_AP700(ap700cmd, ip_ap700[i])

# Custom MQTT message callback
def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")
  
  data = json.loads(message.payload)
  intensity_ap700 = data['state']['desired']['AP700']['intensity']
  print('intensity: ')
  print intensity_ap700
  color_ap700 = data['state']['desired']['AP700']['color']
  print('color: ')
  print color_ap700
  
  cmd_ap700(intensity_ap700, color_ap700)

while True:
  myAWSIoTMQTTClient.subscribe(MY_TOPIC, 0, customCallback)

time.sleep(2)
