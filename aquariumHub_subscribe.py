import os
import time
import json
import datetime
import AWSIoTPythonSDK
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import serial
import subprocess
import inspect
import re
import socket
from pprint import pprint
from exception_handler import GracefulKiller

CMD_A360 = 1;
PORT_AP700 = 8899 # port of ap700
ip_ap700 = [] # list for ip of ap700
iffound_ap700 = False

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

#stdout is the stdout of the system call
#return True/False if ap700 is/isn't found
def findap700(stdout):
  iffound_ap700 = False
    
  for line in stdout.readlines():
    temp = re.split(" +", line)
    print(temp)

    if(len(temp) == 6):
      #if app700 is in the list of dhcp lease
      if(temp[3].find('ac:cf:23')>-1):
        print('ap700 is found')
        ip_ap700.append(temp[0]) #Add an ip of an ap700 to the end of the list "ip_ap700"
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
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # define socket type TCP
  print "connecting to ap700"
  try:
    client.connect((ip_ap700, PORT_AP700))
    client.sendall(bytearray(ap700cmd))
    #print("test = " + ap700cmd)
  except Exception as e: 
    print("something's wrong with %s:%d. Exception is %s" % (ip_ap700, PORT_AP700, e))
  finally:
    client.close()

def cmd_ap700(intensity_ap700, color_ap700):
  #system call for the list of dhcp lease
  SYSCMD = 'cat /proc/net/arp'
  print(SYSCMD)
  process = subprocess.Popen(SYSCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  #find ap700 ip and store it into global list 'ip_ap700'
  findap700(process.stdout)
  returnValue = process.wait()

  data = [0x01, 0x00 , 0x10 , intensity_ap700, color_ap700]
  
  if(intensity_ap700 == 0):
    data = [01,00,01,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,00,00,00,00,00,0]
  
  #generate command for ap700 to set light intensity and color
  ap700cmd = genCmd(data)
  print "command of ap700: "
  pprint(ap700cmd)
  
  for i in range(0, len(ip_ap700), 1):
    sendCmd_AP700(ap700cmd, ip_ap700[i])

# Custom MQTT message callback
def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")
  
  # subscribe shadow topic and take actions for commands of ap700
  try:
    data = json.loads(message.payload)
    intensity_ap700 = data['current']['state']['desired']['AP700']['intensity']
    print('ap700_intensity: ')
    print intensity_ap700
    color_ap700 = data['current']['state']['desired']['AP700']['color']
    print('ap700_color: ')
    print color_ap700
    cmd_ap700(intensity_ap700, color_ap700)
  except Exception as e:
    print("Something wrong while executing commands of ap700. Exception is %s" % (e))
  
  # subscribe shadow topic and take actions for commands of a360
  try:
    intensity_a360 = data['current']['state']['desired']['A360']['intensity']
    print('a360_intensity: ')
    print intensity_a360
    color_a360 = data['current']['state']['desired']['A360']['color']
    print('a360_color: ')
    print color_a360

    myport = serial.Serial("/dev/ttyS0", 57600, timeout= 0.5 )
    jsonObject = json.dumps({"cmd":CMD_A360, "intensity":intensity_a360, "color":color_a360})
    myport.write(jsonObject)
    myport.close()
  except Exception as e:
    print("Something wrong while executing commands of a360. Exception is %s" % (e))
    pass
    
TOPIC_SHADOW = "$aws/things/AquariumHub/shadow/update/documents"

killer = GracefulKiller()
while True:
  if killer.kill_now:
    break
  # subscribe to shadow update
  ip_ap700 = []
  try:
    myAWSIoTMQTTClient.subscribe(TOPIC_SHADOW, 0, customCallback)
  except Exception as e:
    print(e)
    pass
  time.sleep(0.2)
    
print "Stopped"
myAWSIoTMQTTClient.disconnect()
