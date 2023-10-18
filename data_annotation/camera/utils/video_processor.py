import os
import subprocess
import cv2
import pyaudio
import wave
import datetime
import speech_recognition as sr

class Video_Processor:

    def __init__(self, save_location: str):
        self.__current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.__save_loc = os.path.join(save_location, self.__current_datetime)
        if not os.path.exists(self.__save_loc):
            os.makedirs(self.__save_loc)
        os.chdir(self.__save_loc)
        self.__FRAME_WIDTH = 640
        self.__FRAME_HEIGHT = 480
        self.__FPS = 30

        self.__audio_sample_rate = 44100
        self.__audio_format = pyaudio.paInt16
        self.__audio_channels = 2

        self.__vw = cv2.VideoWriter(f'{self.__current_datetime}.mp4', cv2.VideoWriter_fourcc(*"mp4v"), self.__FPS, (self.__FRAME_WIDTH, self.__FRAME_HEIGHT))
        self.__wf = wave.open(f'{self.__current_datetime}.wav', 'wb')
        self.__wf.setnchannels(self.__audio_channels)
        self.__wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.__audio_format))
        self.__wf.setframerate(self.__audio_sample_rate)

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