
import sys
import pprint
import time

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
