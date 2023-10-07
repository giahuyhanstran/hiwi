import asyncio
import json
import base64
import binascii
import datetime
from bleak import BleakScanner
import paho.mqtt.client as mqtt
from random import choice

scanresults_topic = "datahub/{}/scanresults"
control_topic = "datahub/{}/control"
manufacturer_id = 0x072C  # Replace with your manufacturer ID

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode()  # encode bytes to base64 and decode to string
        return json.JSONEncoder.default(self, obj)

class BLEScanner:
    def __init__(self):
        self.buffered_data = []

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {str(rc)}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")

    def on_message(self, client, userdata, message):
        msg = json.loads(message.payload)
        print(msg)

    def detection_callback(self, device, advertisement_data):
        if manufacturer_id not in advertisement_data.manufacturer_data:
            return

        raw_prefix = "0201060302B6FD16FF2C07"
        raw_suffix = binascii.hexlify(advertisement_data.manufacturer_data.get(manufacturer_id, b'')).decode()
        raw_combined = raw_prefix + raw_suffix

        data = {
            "rssi": advertisement_data.rssi,
            "mac": device.address,
            "manid": format(manufacturer_id, '04X'),
            "raw": raw_combined,
            "port": "BlueI",
            "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "uuid": "FDB6"  # Add logic here to extract the UUID from advertisement data if needed.
        }
        self.buffered_data.append(data)

    async def run(self):
        device_id = "".join(choice("0123456789") for _ in range(15))

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message
        client.connect("localhost", 1883, 60)
        client.subscribe(control_topic.format(device_id))
        client.loop_start()

        scanner = BleakScanner(detection_callback=self.detection_callback)
        await scanner.start()

        while True:
            await asyncio.sleep(0.1)  # sleep for 1 second before the next iteration
            if self.buffered_data:  # if buffer is not empty
                topic = scanresults_topic.format(device_id)
                payload = {
                    "data": self.buffered_data,
                    "type": "advertisements"
                }
                client.publish(topic, json.dumps(payload, cls=CustomJSONEncoder))
                self.buffered_data = []  # clear the buffer after sending


if __name__ == "__main__":
    scanner = BLEScanner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scanner.run())
