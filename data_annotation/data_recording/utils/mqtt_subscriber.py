import yaml
import paho.mqtt.client as mqtt
from utils.decoder import PayloadDecoder
from random import randint
import threading
from threading import Thread
from numpy import sqrt
import time
from os import listdir, makedirs
from os.path import isfile, join, exists
import json
import uuid
import struct
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import keyboard
import shutil

class MQTTSubscriber:
    """A class to connect to the MQTT broker."""

    def __init__(self, config: dict, args, path: str = 'matrix_data/'):
        self.__stop_flag = False
        self.__stop_lock = threading.Lock()
        self.__datetime = None
        self.__cfg: dict = config
        self.__args = args
        self.__save_loc = self.__args.save_loc + '/'
        self.__zones: list = [item for item in config if 'ZONE' in item]
        self.__subtopics: list = self.__cfg['SUBTOPIC']
        self.__topic: list[tuple[str, int]] = [(f"chip/{self.__cfg[zone]['MAC_ADDRESS']}/{subtopic}", 0) 
                                         for zone in self.__zones for subtopic in self.__subtopics 
                                         if self.__is_wanted(self.__cfg[zone]['MAC_ADDRESS'])]
        self.__topic.append(("heartbeat/#", 0))
        self.__heartbeats: dict[str, tuple[int, str, str] | None] = {}
        self.__sensor_names: list[str] = []
        self.__decoder = PayloadDecoder()
        self.__path: str = path
        if exists(self.__path):
            shutil.rmtree(self.__path)
        makedirs(self.__path)        
        self.__readings: dict = self.__cfg['READING']
        self.__client: mqtt.Client = mqtt.Client(
            client_id=self.__cfg['MQTT']['USERNAME'] + '_' + str(randint(1, 1000000)))
        self.__client.username_pw_set(username=self.__cfg['MQTT']['USERNAME'], password=self.__cfg['MQTT']['PASSWORD'])
        self.__client.on_message = self.__on_message
        self.__client.message_callback_add('chip/#', self.__on_message_data)
        self.__client.message_callback_add('heartbeat/#', self.__on_message_heartbeat)
        # for accessing sensor data from inside smartlab
        self.__client.connect(host=self.__args.ip, port=self.__args.port)
        # for accessing data from outside the smartlab via SSH tunnel (using port 1883)
        # ssh username@elias -N -v -L 1883:192.168.1.80:1883
        # self.__client.connect(host='localhost', port=self.__cfg['MQTT']['PORT'])
        print('Connected to MQTT broker...')
        self.__client.subscribe(self.__topic)
        print('Subscribed to topics...')

    def __is_wanted(self, sensor_mac: str) -> bool :
        """
        Decides, based off the arguments 'include' and 'exclude' provided (optional), 
        if the messages of a sensor unit are needed or not.
        
        Args:
            sensor_mac: The mac address of the sensor unit.
            
        Returns:
            True or False, based off, if data of a sensor unit is wanted.
        """

        sensor_unit_name: str = self.__get_sensor_unit_name(sensor_mac)
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
        print('Unknown message received')
        
    def __on_message_data(self, client, userdata, message): 
        """
        Function to be triggered when a new message arrives at the client. Decodes new incoming data and saves it to
        the corresponding csv file.

        Args:
            client:
            userdata:
            message: The message (plain JSON) to be decoded and saved.

        """
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        payload = yaml.load(str(message.payload.decode("utf-8")), Loader=yaml.FullLoader)
        data = self.__decoder.decode_payload(payload)

        # TODO Handle accel data -> data['accel_vector']
        if 'thermal_readings' in data.keys():
            reading = 'thermal'
        elif 'tof_readings' in data.keys():
            reading = 'tof'
        else:
            return

        sensor_mac: str = message.topic.split('/')[1]
        # timestamp = payload['captured_at']
        sensor_name = self.__get_sensor_name(sensor_mac, data)
                      
        if not (self.__args.type == reading or self.__args.type == None):
            return
        
        print("message_received")
        print("message topic: ", message.topic)

        if not sensor_name in self.__sensor_names:
            self.__sensor_names.append(sensor_name)
            if not exists(f'{self.__path}{sensor_name}/'):
                makedirs(f'{self.__path}{sensor_name}/')

        self.__update_heartbeats(current_datetime, interval=1)

        sensor_data = {
            "SENSOR_NAME": sensor_name, 
            "DATA": data[reading + '_readings'],
            "HEARTBEATS": self.__heartbeats
        }

        json_hb_data = json.dumps(sensor_data, indent=4)
        file_path = f'{self.__path}{sensor_name}/{current_datetime}.json'

        with open(file_path, 'w') as file:
            file.write(json_hb_data)

    def __on_message_heartbeat(self, client, userdata, message):
            
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
            device_name = message.topic.split('/')[-1]

            # Unpack payload
            frame_bytes = message.payload[:4]
            uuid_bytes = message.payload[4:]            
            frame = struct.unpack('!I', frame_bytes)[0]
            uuid_str = str(uuid.UUID(bytes=uuid_bytes))

            self.__heartbeats[uuid_str] = [frame, current_datetime, device_name]
                
    def receive_messages(self, rc_time: int = None):
        """Function to receive/handle incoming MQTT messages.

        Args:
            rc_time: The time for which you want to record data.
        """
        self.__datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if rc_time is None:
            t = Thread(target=self.__client.loop_forever)
            t.start()
            while not self.__stop_flag:
                pass
            self.__client.disconnect()
            self.__client.loop_stop()
        else:
            def _collector():
                start_time = time.time()
                self.__client.loop_start()
                while True:
                    if time.time() - start_time >= rc_time or self.__stop_flag:
                        self.__client.disconnect()
                        self.__client.loop_stop()
                        break

            t = Thread(target=_collector)
            t.start()

        self.__json_to_csv()
        self.__del_json()
   
    def stop_receiving(self):
        with self.__stop_lock:
            self.__stop_flag = True

    def __update_heartbeats(self, current_datetime: str, interval: int):

        current_datetime = datetime.strptime(current_datetime, "%Y-%m-%d_%H-%M-%S-%f")

        for key in self.__heartbeats.keys():
            time_entry = datetime.strptime(self.__heartbeats[key][1], "%Y-%m-%d_%H-%M-%S-%f")
            if current_datetime > time_entry + timedelta(seconds=interval):
                self.__heartbeats[key][0] = None

    def __json_to_csv(self):

        csv_path = f"{self.__datetime}_sensor_data"

        save_loc = self.__save_loc + csv_path

        if not exists(save_loc):
            makedirs(save_loc)

        print('Adding received heartbeats to data ...')
        data_folder: list[str] = [folder for folder in listdir(f'{self.__path}') if not isfile(join(self.__path, folder))]

        if not data_folder:
            print("No data found.")
            return
        
        for folder in data_folder:

            path: str = f'{self.__path}{folder}/'
            data_files: list[str] = [file for file in listdir(path) if isfile(join(path, file))]
            
            # TODO load last file, because this contains all Heartbeats that emerged during recording
            # TODO problem: what if last message does not contain all data points? e.g. 4 instead of 9 (3x3)
            with open(join(path, data_files[-1]), 'r') as file:
                payload: dict = json.load(file)
            pixel_data_len = len(payload['DATA'])
            hb_device_names: list = payload['HEARTBEATS'].keys()

            abbreviation = folder.split('_')[0]
            column_names = [abbreviation + str(i) for i in range(pixel_data_len)]
            column_names.append('time')
            column_names.extend(hb_device_names)
            df = pd.DataFrame(columns=column_names)

            for file in data_files:
                with open(join(path, file), 'r') as item:
                    payload: dict = json.load(item)
                data = payload['DATA']
                data.append(file[:-5])
                for key in payload['HEARTBEATS'].keys():
                    data.append(payload['HEARTBEATS'][key][0])                                                        
                df.loc[len(df)] = data
            
            df.to_csv(f"{save_loc}/{folder}.csv", index=False)

    def __get_sensor_unit_name(self, sensor_mac: str) -> str:
        """Extracts the sensor unit name corresponding to it's mac address.
        If no name exits, ValueError is thrown and None returned.
        
        Args:
            sensor_mac: The mac address of the sensor unit.
            
        Returns:
            str: The name of the sensor unit as a string.
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

    def __get_sensor_name(self, sensor_mac: str, sensor_data: dict) -> str:
        """Method to extract the name (=type) of the sensor out of the JSON data.

        Args:
            sensor_mac: The mac address of the sensor unit.
            sensor_data: The actual sensor data/message.

        Returns:
            str: The name of the sensor. That includes the type of data and the sensor unit name.
        """
        try:
            for reading in self.__readings.keys():
                if f'{reading.lower()}_readings' in sensor_data.keys():
                    column_name = self.__readings[reading]
                    return column_name + self.__get_sensor_unit_name(sensor_mac)

            raise ValueError("No matching reading category found in sensor_data.keys().")
        except ValueError as e:
            print(f"Error: {str(e)}")
            return ""

    def __del_json(self):
        try:
            shutil.rmtree(self.__path)
            print(f"Folder '{self.__path}' and its contents have been successfully deleted.")
        except OSError as e:
            print(f"Error deleting folder '{self.__path}': {e}")