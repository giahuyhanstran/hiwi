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
import json


class MQTTSubscriber:
    """A class to connect to the MQTT broker."""

    def __init__(self, config: dict, args, path: str = 'matrix_data/'):
        self.__cfg : dict = config
        self.__args = args
        self.__heartbeat = None
        self.__zones: list = [item for item in config if 'ZONE' in item]
        self.__subtopics: list = self.__cfg['SUBTOPIC']
        self.__topic: tuple(str, int) = [(f"chip/{self.__cfg[zone]['MAC_ADDRESS']}/{subtopic}", 0) 
                                         for zone in self.__zones for subtopic in self.__subtopics 
                                         if self.__is_wanted(self.__cfg[zone]['MAC_ADDRESS'])]
        self.__topic.append(("heartbeat", 0))
        self.__decoder = PayloadDecoder()
        self.__path: str = path
        if not exists(self.__path):
            makedirs(self.__path)        
        self.__category: list = self.__cfg['READING']['CATEGORY']
        self.__column_name: list = self.__cfg['READING']['COLUMN_NAME']
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

    def __write_data(self, file_name: str, timestamp, files: list[str], data: dict, reading: str): #TODO add timestamp datatype

        with open(self.__path + file_name, 'a', newline='') as f:
            print('Writing to ', file_name)
            colum_names = [self.__column_name[self.__category.index(reading)] + str(i) for i in range(len(data[reading]))]
            colum_names.append('time')
            colum_names.append('frame')
            readings = data[reading]
            readings.append(timestamp)
            readings.append(self.__heartbeat)
            data = dict(zip(colum_names, readings))
            w = DictWriter(f, fieldnames=data.keys()) # for Py 3.7+ .keys() order is based on insertion and guaranteed the same
            if not file_name in files:
                w.writeheader()
            w.writerow(data)
            f.close()

    def __is_wanted(self, sensor_mac: str) -> bool :
        """Decides, based off the arguments 'include' and 'exclude' provided (optional), 
        if the messages of a sensor unit are needed or not.
        
        Args:
            sensor_mac: The mac adress of the sensor unit.
            
        Returns:
            True or False, based off, if data of a sensor unit is wanted"""

        sensor_unit_name: str = self._get_sensor_unit_name(sensor_mac)
        in_is_empty: bool = self.__args.include == None
        out_is_empty: bool = self.__args.exclude == None

        # default: message is wanted
        if in_is_empty and out_is_empty:
            return True

        if in_is_empty:
            message_out: bool = any(item in self.__args.exclude for item in [sensor_mac, sensor_unit_name])
            if not message_out:
                return True
            return False
        else:
            message_in: bool = any(item in self.__args.include for item in [sensor_mac, sensor_unit_name])
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

        sensor_mac: str = message.topic.split('/')[1]
        timestamp = payload['captured_at']

        file_name: str = self._get_sensor_name(sensor_mac, data) + '.csv'
        files: list[str] = [f for f in listdir(self.__path) if isfile(join(self.__path, f))]
        
        if 'tof_readings' in data.keys() and (self.__args.type == 'tof' or self.__args.type == None):
            print("message_received")
            print("message topic: ", message.topic)
            self.__write_data(file_name, timestamp, files, data, 'tof_readings')

        elif 'thermal_readings' in data.keys() and (self.__args.type == 'thermal' or self.__args.type == None):
            print("message_received")
            print("message topic: ", message.topic)
            self.__write_data(file_name, timestamp, files, data, 'thermal_readings')

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
    
    #TODO What is this functions use?
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
    
    def _get_sensor_unit_name(self, sensor_mac: str) -> str:
        """Extracts the sensor unit name corresponding to it's mac address.
        If no name exits, ValueError is thrown and None returned.
        
        Args:
            sensor_mac: The mac adress of the sensor unit.
            
        Returns:
            The name of the sensor unit as a string
        """
        try:
            name = None
            for zone, zone_info in self.__cfg.items():
                if 'ZONE' in zone and zone_info["MAC_ADDRESS"] == sensor_mac:
                    name = zone_info["NAME"]
                    break
            if name is None:
                raise ValueError("No name found for the given MAC_ADDRESS.")
            return name
        except ValueError as e:
            print(f"Error: {str(e)}")
            return None

    def _get_sensor_name(self, sensor_mac: str, sensor_data: dict) -> str:
        """Method to extract the name (=type) of the sensor out of the JSON data.

        Args:
            sensor_mac: The mac adress of the sensor unit.
            sensor_data: The actual sensor data/message.

        Returns:
            The name of the sensor as a string.
        """
        try:
            for reading in self.__category:
                if reading in sensor_data.keys():
                    index = self.__category.index(reading)
                    column_name = self.__column_name[index]
                    return column_name + self._get_sensor_unit_name(sensor_mac)

            raise ValueError("No matching reading category found in sensor_data.keys().")
        except ValueError as e:
            print(f"Error: {str(e)}")
            return ""
