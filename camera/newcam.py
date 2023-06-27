import json
import shutil
import subprocess
import cv2
import pyaudio
import wave
import datetime
import os
import pickle


# TODO optional argparse parameters from b4
def record_video_audio(video_output_file, audio_output_file, current_date, dir_path):
    # Create a folder to stor files
    os.makedirs(current_date)

    video_output_file = os.path.join(current_date, video_output_file)
    audio_output_file = os.path.join(current_date, audio_output_file)

    cap = cv2.VideoCapture(0)

    # default settings
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    audio_format = pyaudio.paInt16
    audio_channels = 1
    audio_sample_rate = 44100
    audio_chunk_size = int(audio_sample_rate / fps)

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format,
                    channels=audio_channels,
                    rate=audio_sample_rate,
                    input=True,
                    frames_per_buffer=audio_chunk_size)

    video_writer = cv2.VideoWriter(video_output_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height))
    audio_frames = []
    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_frame += 1
        file_path = os.path.join(dir_path, f"{current_frame}.pickle")

        video_writer.write(frame)

        audio_data = stream.read(audio_chunk_size)
        audio_frames.append(audio_data)

        video_data = (frame, audio_data)
        with open(file_path, 'wb') as file:
            pickle.dump(video_data, file)
            print(type(video_data))

        cv2.imshow("Camera", frame)

        # break con
        if cv2.waitKey(1) == ord('q'):
            break

    # cleanup vid
    video_writer.release()
    cap.release()
    cv2.destroyAllWindows()

    print(len(audio_frames))
    audio_frames = audio_frames[:len(audio_frames) // fps * fps]
    print(len(audio_frames))

    # Save audio frames in audio file
    wf = wave.open(audio_output_file, 'wb')
    wf.setnchannels(audio_channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(audio_sample_rate)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

    # clean up audio
    stream.stop_stream()
    stream.close()
    p.terminate()

    # print(audio_frames)


# ffmpeg command to merge audio and vid
def merge_audio_video(output_file, current_date):
    video_file = os.path.join(current_date, 'output_video.mp4')
    audio_file = os.path.join(current_date, 'output_audio.wav')

    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    subprocess.call(command, shell=True)


current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# save everything in folder
video_output_file = 'output_video.mp4'
audio_output_file = 'output_audio.wav'

audio_file_path = os.path.join(current_date, audio_output_file)
directory_path = os.path.join(os.getcwd(), current_date)

record_video_audio(video_output_file, audio_output_file, current_date, directory_path)
merge_audio_video('merged_output.mp4', current_date)

file_path_merged = os.path.join(os.getcwd(), "merged_output.mp4")

if not os.path.exists(directory_path):
    os.makedirs(directory_path)

shutil.move(file_path_merged, directory_path)

# TODO Clean up code
# TODO impl. partition into frames w/  ffmpeg
# TODO MQTT to sync up 4 later
