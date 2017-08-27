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
import re
import socket
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
    client.settimeout(5)
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
<<<<<<< HEAD
        data = [01,00,01,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,00,00,00,00,00,0]
=======
        data = bytearray([01,00,01,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,00,00,00,00,00,0])
>>>>>>> a018ce4e65576b77e6b74bd06b1fe7044f64de4c
    
    #generate command for ap700 to set light intensity and color
    ap700cmd = genCmd(data)
    print "command of ap700: "
    pprint(ap700cmd)
    
    for i in range(0, len(ip_ap700), 1):
        sendCmd_AP700(ap700cmd, ip_ap700[i])
  
count = 0
  
while(count < 10):
    ip_ap700 = []
    print('count: ' + str(count+1))
    cmd_ap700(10*count, 10*count)
    count = count + 1
    time.sleep(2)
