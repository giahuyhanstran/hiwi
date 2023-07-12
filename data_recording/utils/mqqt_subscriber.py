import yaml
import paho.mqtt.client as mqtt
from utils.decoder import PayloadDecoder
from random import randint
from threading import Thread
from numpy import sqrt
import time
from os import listdir, makedirs
from os.path import isfile, join, exists
from csv import DictWriter


class MQTTSubscriber:
    """A class to connect to the MQTT broker."""

    def __init__(self, config: dict, args, path: str = 'matrix_data/'):
        self.__cfg = config
        self.__args = args
        self.__heartbeat = None
        self.__sensor_types = {'EC:8D:88:35:49:F9': '_foot_new',
                               'F8:60:BB:C0:58:A6': '_foot_old',
                               'F0:4C:E9:43:98:AF': 'ToF_right',
                               'CC:F4:CF:F7:44:85': 'ToF_left'}
        self.__topic = [
            (f"chip/{self.__cfg['ZONE_0']['MAC_ADDRESS']}/idle_patientzone", 0),
            (f"chip/{self.__cfg['ZONE_0']['MAC_ADDRESS']}/data/patient_zone/thermal/event", 0),
            # (f"chip/{cfg['ZONE_0']['MAC_ADDRESS']}/data/patient_zone/thermal/sub_event", 0),
            (f"chip/{self.__cfg['ZONE_1']['MAC_ADDRESS']}/idle_patientzone", 0),
            (f"chip/{self.__cfg['ZONE_1']['MAC_ADDRESS']}/data/patient_zone/thermal/event", 0),
            (f"chip/{self.__cfg['ZONE_2']['MAC_ADDRESS']}/idle_patientzone", 0),
            (f"chip/{self.__cfg['ZONE_3']['MAC_ADDRESS']}/idle_patientzone", 0),
            ("Heartbeat", 0) # subscribe always to "Heartbeat", contains frame counter of rgb camera
        ]
        self.__decoder = PayloadDecoder()
        self.__path = path
        if not exists(self.__path):
            makedirs(self.__path)
        self.__client: mqtt.Client = mqtt.Client(
            client_id=self.__cfg['MQTT']['USERNAME'] + '_' + str(randint(1, 1000000)))
        self.__client.username_pw_set(username=self.__cfg['MQTT']['USERNAME'], password=self.__cfg['MQTT']['PASSWORD'])
        self.__client.on_message = self.__on_message
        # for accessing sensor data from inside smartlab
        self.__client.connect(host=self.__cfg['MQTT']['ADDRESS'], port=self.__cfg['MQTT']['PORT'])
        # for accessing data from outside the smartlab via SSH tunnel (using port 1883)
        # ssh username@elias -N -v -L 1883:192.168.1.80:1883
        # self.__client.connect(host='localhost', port=self.__cfg['MQTT']['PORT'])
        print('Connected to MQTT broker...')
        self.__client.subscribe(self.__topic)
        print('Subscribed to topics...')

    def write_data(self, file_name, timestamp, files, data: dict, type_index: int):

        types = ['tof_readings', 'thermal_readings']
        types_header = ['ToFZ_', 'TZ_']
        with open(self.__path + file_name, 'a', newline='') as f:
            print('Writing to ', file_name)
            indices = [types_header[type_index] + str(i) for i in range(len(data[types[type_index]]))]
            indices.append('time')
            indices.append('frame')
            readings = data[types[type_index]]
            readings.append(timestamp)
            readings.append(self.__heartbeat)
            data = dict(zip(indices, readings))
            w = DictWriter(f, fieldnames=data.keys())
            if not file_name in files:
                w.writeheader()
            w.writerow(data)
            f.close()

    def is_wanted(self, sensor_mac: str, sensor_name: str) -> bool :

        in_is_empty = len(self.__args.include) == 0
        message_in = any(item in self.__args.include for item in [sensor_mac, sensor_name])
        message_out = any(item in self.__args.exclude for item in [sensor_mac, sensor_name])
        
        if in_is_empty:
            if not message_out:
                return True
            return False
        else:
            if message_in:
                return True
            return False

    def __on_message(self, client, userdata, message):
        """Function to be triggered when a new message arrives at the client. Decodes new incoming data and saves it to
        the corresponding csv file.

        Args:
            client:
            userdata:
            message: The message (plain JSON) to be decoded and saved.

        """
        if message.topic == "Heartbeat":
            self.__heartbeat = message.payload.decode("utf-8")
            return
        
        payload = yaml.load(str(message.payload.decode("utf-8")), Loader=yaml.FullLoader)
        data = self.__decoder.decode_payload(payload)

        sensor_mac = message.topic.split('/')[1]
        sensor_name = self._get_sensor_name(sensor_mac, data)
        timestamp = payload['captured_at']

        file_name = sensor_name + '.csv'
        files = [f for f in listdir(self.__path) if isfile(join(self.__path, f))]

        if not self.is_wanted(sensor_mac, sensor_name):
            return
        
        if 'tof_readings' in data.keys() and (self.__args.type == 'tof' or self.__args.type == None):
            print("message_received")
            print("message topic: ", message.topic)
            self.write_data(file_name, timestamp, files, data, 0)

        elif 'thermal_readings' in data.keys() and (self.__args.type == 'thermal' or self.__args.type == None):
            print("message_received")
            print("message topic: ", message.topic)
            self.write_data(file_name, timestamp, files, data, 1)

    def receive_messages(self, rc_time: int = None):
        """Function to receive/handle incoming MQTT messages.

        Args:
            rc_time: The time for which you want to record data.

        """
        if rc_time is None:
            t = Thread(target=self.__client.loop_forever())
            t.start()
        else:
            def _collector():
                start_time = time.time()
                run = True
                self.__client.loop_start()
                while run:
                    if time.time() - start_time >= rc_time:
                        self.__client.disconnect()
                        self.__client.loop_stop()
                        run = False

            t = Thread(target=_collector())
            t.start()

    @staticmethod
    def _get_indices(data: list) -> list:
        """Method to generate indices (column names) for the csv files.

        Args:
            data: The data to be stored.

        Returns:
            A list with all necessary column names.

        """
        indices = []
        max_index = int(sqrt(len(data)))
        for i in range(1, max_index + 1):
            for j in range(1, max_index + 1):
                indices.append((i, j))
        return indices

    def _get_sensor_name(self, sensor_mac: str, sensor_data: dict) -> str:
        """Method to extract the name (=type) of the sensor out of the JSON data.

        Args:
            sensor_mac: The mac adress of the sensor.
            sensor_data: The actual sensor data/message.

        Returns:
            The name of the sensor as a string.
        """
        keys = sensor_data.keys()
        sensor_type = self.__sensor_types[sensor_mac]
        if sensor_type == "_foot_new" or sensor_type == "_foot_old":
            if "tof_readings" in keys:
                return 'ToF' + sensor_type
            else:
                return 'thermal' + sensor_type
        else:
            return sensor_type
