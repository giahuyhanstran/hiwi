# TODO concate Video
import argparse
import os
import pickle
import subprocess
import time
import cv2
import pyaudio
import wave
import paho.mqtt.client as mqtt
import datetime
import keyboard
import speech_recognition as sr


class Video_Processor:

    def __init__(self, save_location: str, length: int = None):
        self.__time_done = False
        self.__current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.__save_loc = os.path.join(save_location, self.__current_datetime)
        if not os.path.exists(self.__save_loc):
            os.makedirs(self.__save_loc)
        os.chdir(self.__save_loc)
        self.__FRAME_WIDTH = 640
        self.__FRAME_HEIGHT = 480
        self.__FPS = 30

        self.__audio_sample_rate = 44100
        self.__audio_chunk_size = int(self.__audio_sample_rate / self.__FPS)
        self.__audio_format = pyaudio.paInt16
        self.__audio_channels = 2

        self.__vw = cv2.VideoWriter(f'{self.__current_datetime}.mp4', cv2.VideoWriter_fourcc(*"mp4v"), self.__FPS, (self.__FRAME_WIDTH, self.__FRAME_HEIGHT))
        self.__wf = wave.open(f'{self.__current_datetime}.wav', 'wb')
        self.__wf.setnchannels(self.__audio_channels)
        self.__wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.__audio_format))
        self.__wf.setframerate(self.__audio_sample_rate)

        self.__length = length

        #mqtt
        self.__address = '192.168.1.80'
        self.__port = 1883
        self.__address_l = "localhost"
        self.__client = mqtt.Client("Laptop")
        self.__topic = "Camera"

    def receive_mqtt_messages(self):

        self.__client.connect(host=self.__address_l, port=self.__port)
        self.__client.loop_start()
        self.__client.subscribe(self.__topic)
        self.__client.on_message = self.__on_message

        # Loop until the stop key is pressed
        while True:
            # Check for a key press
            key = cv2.waitKey(1) & 0xFF

            # extra time to start and catch up with record_camera.py
            if self.__length is not None:
                if self.__time_check(self.__length + 30):
                    self.__time_done = True

            # Break the loop if the stop key is pressed
            if keyboard.is_pressed('s') or self.__time_done:
                break

        self.__client.loop_stop()

        self.__vw.release()
        self.__wf.close()

    def __on_message(self, client, userdata, message):

        payload = message.payload
        content = pickle.loads(payload)
        self.__vw.write(content[0])
        self.__wf.writeframes(content[1])

    def write_data(self, video_frame, audio_chunk):
        self.__vw.write(video_frame)
        self.__wf.writeframes(audio_chunk)

    def stop_writer(self):
        self.__vw.release()
        self.__wf.close()

    def merge_audio_video(self):
        video_file = f'{self.__current_datetime}.mp4'
        audio_file = f'{self.__current_datetime}.wav'
        output_file = f'{self.__current_datetime}_merged.mp4'

        command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
        subprocess.run(command, shell=True)

    def __time_check(self, time_in_seconds):
        start_time = time.time()
        current_time = time.time()
        elapsed_time = current_time - start_time

        while elapsed_time < time_in_seconds:
            current_time = time.time()
            elapsed_time = current_time - start_time

        return True