from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

# Read in command-line parameters
host = "a2bdrinkbnov3t.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "./AWS/root-CA.crt"
certificatePath = "./AWS/AquariumHub.cert.pem"
privateKeyPath = "./AWS/AquariumHub.private.key"

# AWSIoTMQTTShadowClient connection configuration
myShadowClient = AWSIoTMQTTShadowClient("shadowClientID")
myShadowClient.configureEndpoint(host, 8883)
myShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
myShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")
	
myShadowClient.connect()

# Create a device shadow instance using persistent subscription
myDeviceShadow = myShadowClient.createShadowHandlerWithName("Bot", True)

# Shadow operations
myDeviceShadow.shadowUpdate(
{
    "state" : {
        "desired" : {
            "color" : "red",
            "power" : "on"
         }
     }
}, customCallback, 5)