import paho.mqtt.client as mqtt
import time
import uuid
import struct
from random import randint

mqttBroker = "localhost"
client = mqtt.Client("Topi")
client.connect(host = mqttBroker, port = 1883)
uuid_bytes1 = uuid.UUID('1aad35ef-4fac-4bf9-ae2f-5b2af6ae5ddd').bytes
uuid_bytes2 = uuid.UUID(str(uuid.uuid4())).bytes
frame_counter1 = 0
frame_counter2 = 1000

topic1 = "heartbeat/device1"
topic2 = f"heartbeat/device{randint(2, 100000)}"


while True:

    frame_counter_bytes1 = struct.pack('!I', frame_counter1)
    frame_counter_bytes2 = struct.pack('!I', frame_counter2)

    data1 = bytearray(frame_counter_bytes1 + uuid_bytes1)
    data2 = bytearray(frame_counter_bytes2 + uuid_bytes2)



    client.publish(topic1, data1)
    client.publish(topic2, data2)
    print(f"Just pusblished {frame_counter1} to topic {topic1}")
    print(f"Just pusblished {frame_counter2} to topic {topic2}")
    frame_counter1 += 1
    frame_counter2 += 1
    time.sleep(1)