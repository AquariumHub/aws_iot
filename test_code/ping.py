import os
HOST_PREFIX = "192.168.1."

for x in range(2, 255, 1):
	response = os.system("ping -c 1 " + HOST_PREFIX + str(x))
	
	if response == 0:
		print(HOST_PREFIX + str(x) + " is alive")