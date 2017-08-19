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

PORT_AP700 = 8899
ip_ap700 = [] # list for ip of ap700

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
  print "connecting to ap700"
  if(client.connect((ip_ap700, PORT_AP700))):
    print "ap700 connected"
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
  
count = 0
  
while(count < 10):
  print('count: ' + str(count+1))
  cmd_ap700(10*count, 10*count)
  count = count + 1

time.sleep(2)
