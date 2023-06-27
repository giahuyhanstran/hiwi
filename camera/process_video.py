# TODO concate Video
import os
import pickle
import re

import cv2
import subprocess

frame_width = 640
frame_height = 480
fps = 30
merged_data = {}
directory = '2023-06-28_01-02-36'

video_writer = cv2.VideoWriter(f'{directory}_recreated.mp4', cv2.VideoWriter_fourcc(*"mp4v"), fps,
                               (frame_width, frame_height))


def combine_frames_with_audio(frame_rate, image_pattern, audio_file, output_file):
    ffmpeg_cmd = [
        "ffmpeg",
        "-r", str(frame_rate),
        "-i", image_pattern,
        "-i", audio_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-vf", f"fps={frame_rate},format=yuv420p",
        output_file
    ]

    subprocess.run(ffmpeg_cmd)

print(os.listdir(directory))
sorted_strings = sorted(os.listdir(directory), key=lambda x: (int(re.match(r'^(\d+)', x).group(0)) if re.match(r'^(\d+)', x) else float('inf'), x))
frame_counter = 1
for filename in sorted_strings:
    if filename.endswith('.pickle'):
        print(filename)
        frame_counter += 1
        file_path = os.path.join(directory, filename)
        with open(file_path, 'rb') as file:
            content = pickle.load(file)
            merged_data[frame_counter] = content

for video in merged_data:
    video_writer.write(merged_data[video][0])
video_writer.release()
