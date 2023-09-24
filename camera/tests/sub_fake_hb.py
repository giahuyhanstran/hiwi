import paho.mqtt.client as mqtt
import time
import struct
import uuid
import datetime
import json
from os import makedirs
from os.path import exists

def on_message(client, userdata, message):
        # Extract the data from the received bytearray

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    device_name = message.topic.split('/')[-1]

    frame_counter_bytes = message.payload[:4]
    uuid_bytes = message.payload[4:]
    
    # Unpack the extracted values
    frame_counter = struct.unpack('!I', frame_counter_bytes)[0]
    uuid_str = str(uuid.UUID(bytes=uuid_bytes))

    if uuid_str in device_uuids:
        hb_device_counter = f'hb-{device_uuids.index(uuid_str)}'
    else:
        device_uuids.append(uuid_str)
        hb_device_counter = f'hb-{device_uuids.index(uuid_str)}'
        if not exists(f'{path}hb/{hb_device_counter}/'):
            makedirs(f'{path}hb/{hb_device_counter}/')


    hb_data = {
    "DEVICE_NAME": device_name,
    "UUID": uuid_str,
    "HEARTBEAT": frame_counter
    }

    json_hb_data = json.dumps(hb_data, indent=4)
    file_path = f'{path}hb/{hb_device_counter}/{current_datetime}.json'

    with open(file_path, 'w') as file:
        file.write(json_hb_data)
    

if __name__ == '__main__':
    path = 'matrix_data/'
    if not exists(path):
        makedirs(path)

    device_uuids = []

    mqttBroker = "localhost"
    client = mqtt.Client("Lapi")
    client.connect(host = mqttBroker, port = 1883)

    client.loop_start()
    client.subscribe("heartbeat/#")
    client.on_message = on_message
    time.sleep(300)    


