# TODO concate Video
import os
import pickle
import re
import cv2
import subprocess
import pyaudio
import wave

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
DIRECTORY = '2023-06-28_08-50-30'
merged_data = {}
vw = cv2.VideoWriter(f'{DIRECTORY}_recreated_video.mp4', cv2.VideoWriter_fourcc(*"mp4v"), FPS,
                     (FRAME_WIDTH, FRAME_HEIGHT))

sorted_pickles = sorted(os.listdir(DIRECTORY), key=lambda x: (
    int(re.match(r'^(\d+)', x).group(0)) if re.match(r'^(\d+)', x) else float('inf'), x))


def unpickle(frame_directory):
    frame_counter = 1
    for filename in sorted_pickles:
        if filename.endswith('.pickle'):
            frame_counter += 1
            file_path = os.path.join(frame_directory, filename)
            with open(file_path, 'rb') as file:
                content = pickle.load(file)
                merged_data[frame_counter] = content


def combine_video(merged_data, video_writer):
    for video in merged_data:
        video_writer.write(merged_data[video][0])
    video_writer.release()


audio_sample_rate = 44100
audio_chunk_size = int(audio_sample_rate / FPS)
audio_format = pyaudio.paInt16
audio_channels = 2


def combine_audio_frames(merged_data):
    audio_frames = []
    for audio in merged_data:
        audio_frames.append(merged_data[audio][1])
    audio_frames = audio_frames[:len(audio_frames) // FPS * FPS]
    print(len(audio_frames))
    wf = wave.open(f'{DIRECTORY}_recreated_audio.wav', 'wb')
    wf.setnchannels(audio_channels)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_format))
    wf.setframerate(audio_sample_rate)
    wf.writeframes(b''.join(audio_frames))
    wf.close()
    pass


def merge_audio_video(output_file):
    video_file = os.path.join(os.getcwd(), f'{DIRECTORY}_recreated_video.mp4')
    audio_file = os.path.join(os.getcwd(), f'{DIRECTORY}_recreated_audio.wav')

    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    subprocess.call(command, shell=True)


unpickle(DIRECTORY)
combine_video(merged_data, vw)
combine_audio_frames(merged_data)
merge_audio_video('merged_output.mp4')
