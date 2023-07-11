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

'''
Note: Script is listening on localhost port 1883 for topic "Camera"
      At first start HiveMQ Broker, then run record_camera.py, then
      run this script. You can use MQTT Explorer to check for data traffic.
'''


def on_message(client, userdata, message):
    global vw
    global wf

    payload = message.payload
    content = pickle.loads(payload)
    vw.write(content[0])
    wf.writeframes(content[1])

def merge_audio_video(output_file):
    video_file = f'{current_date}.mp4'
    audio_file = f'{current_date}.wav'

    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    subprocess.run(command, shell=True)

def transcriber(input_file):

    r = sr.Recognizer()
    file = f"{current_date}.txt"

    with sr.AudioFile(input_file) as source:
        
        audio = r.listen(source) 
        
        try:
            transcription = (r.recognize_google(audio, language="de-DE,en-US"))
            with open(file, "w") as output_file:
                output_file.write(transcription)
        except sr.UnknownValueError:
            # handle unrecognized speech - insert a placeholder
            placeholder = "<unrecognized>"
            with open(file, "w") as output_file:
                output_file.write(placeholder)

def time_check(time_in_seconds):
    start_time = time.time()
    current_time = time.time()
    elapsed_time = current_time - start_time

    while elapsed_time < time_in_seconds:
        current_time = time.time()
        elapsed_time = current_time - start_time

    return True


if __name__ == '__main__':
    time_done = False

    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    DIRECTORY = os.path.join(os.getcwd(), current_date)
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    os.chdir(DIRECTORY)

    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30

    merged_data = {}

    audio_sample_rate = 44100
    audio_chunk_size = int(audio_sample_rate / FPS)
    audio_format = pyaudio.paInt16
    audio_channels = 2

    vw = cv2.VideoWriter(f'{current_date}.mp4', cv2.VideoWriter_fourcc(*"mp4v"), FPS, (FRAME_WIDTH, FRAME_HEIGHT))
    wf = wave.open(f'{current_date}.wav', 'wb')
    wf.setnchannels(audio_channels)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_format))
    wf.setframerate(audio_sample_rate)

    # mqtt
    mqttBroker = "localhost"
    client = mqtt.Client("Laptop")
    client.connect(host=mqttBroker, port=1883)

    client.loop_start()
    client.subscribe("Camera")
    client.on_message = on_message

    parser = argparse.ArgumentParser(description='get frame from mp4')
    parser.add_argument('--length', type=int, help='default until interrupt, else time in seconds')
    args = parser.parse_args()

    length = args.length if args.length is not None else None

    # Loop until the stop key is pressed
    while True:
        # Check for a key press
        key = cv2.waitKey(1) & 0xFF

        # extra time to start and catch up with record_camera.py
        if length is not None:
            if time_check(length + 30):
                time_done = True

        # Break the loop if the stop key is pressed
        if keyboard.is_pressed('s') or time_done:
            break

    client.loop_stop()

    vw.release()
    wf.close()

    merge_audio_video(f'{current_date}_merged.mp4')
    transcriber(f'{current_date}.wav')
