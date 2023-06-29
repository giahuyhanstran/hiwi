# TODO concate Video
import os
import pickle
import cv2
import pyaudio
import wave
import paho.mqtt.client as mqtt
import datetime
import keyboard
from moviepy.editor import VideoFileClip, AudioFileClip

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

# TODO make sure message in right order upon receive
def sort_incoming_messages():
    '''
   sorted_pickles = sorted(os.listdir(DIRECTORY), key=lambda x: (
   int(re.match(r'^(\d+)', x).group(0)) if re.match(r'^(\d+)', x) else float('inf'), x))

    '''
    pass


def merge_audio_video(output_file):
    video = VideoFileClip(f'{current_date}.mp4')
    audio = AudioFileClip(f'{current_date}.wav')
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")



'''
def merge_audio_video(output_file):
    video_file = os.path.join(os.getcwd(), f'{DIRECTORY}_recreated_video.mp4')
    audio_file = os.path.join(os.getcwd(), f'{DIRECTORY}_recreated_audio.wav')

    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    subprocess.call(command, shell=True)
'''

if __name__ == '__main__':

    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    DIRECTORY = os.path.join(os.getcwd(), current_date)
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    os.chdir(DIRECTORY)

    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30

    merged_data = {}
    frame_counter: int = 0

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
    # Loop until the stop key is pressed
    while True:
        # Check for a key press
        key = cv2.waitKey(1) & 0xFF

        # Break the loop if the stop key is pressed
        if keyboard.is_pressed('q'):
            break

    client.loop_stop()

    vw.release()
    wf.close()
    merge_audio_video(f'{current_date}_merged.mp4')
