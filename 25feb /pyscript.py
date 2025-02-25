import paho.mqtt.client as mqtt
import json

broker = "127.0.0.1"  # Localhost broker
topic = "drone/status"
client = mqtt.Client()

client = mqtt.Client()
client.connect(broker, 1883, 60)

# Example drone status update
status = {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 100,
    "battery": 85
}

client.publish(topic, json.dumps(status))
print("Published drone status")
client.disconnect()
