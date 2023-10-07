import paho.mqtt.client as mqtt
import time
import struct
import uuid

def on_message(client, userdata, message):
    # Extract the data from the received bytearray

    print('message received')

    frame_counter_bytes = message.payload[:4]
    uuid_bytes = message.payload[4:]
    
    # Unpack the extracted values
    frame_counter = struct.unpack('!I', frame_counter_bytes)[0]
    uuid_str = str(uuid.UUID(bytes=uuid_bytes))

    print(uuid_str)
    print(frame_counter)
    print('')
    

if __name__ == '__main__':

    mqttBroker = "localhost"
    client = mqtt.Client("Lapi")
    client.on_message = on_message
    client.connect(host = mqttBroker, port = 1883)
    print('connected')
    
    client.loop_start()
    client.subscribe("heartbeat/#")
    print('subscribed')
    
    time.sleep(300)    


