import shutil
import subprocess
import cv2
import pyaudio
import wave
import datetime
import os
import speech_recognition as sr

# TODO optional argparse parameters from b4
def record_video_audio(video_output_file, audio_output_file, folder_name):
    # Create a folder to stor files
    os.makedirs(folder_name)

    video_output_file = os.path.join(folder_name, video_output_file)
    audio_output_file = os.path.join(folder_name, audio_output_file)

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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        video_writer.write(frame)

        audio_data = stream.read(audio_chunk_size)
        audio_frames.append(audio_data)

        cv2.imshow("Camera", frame)

        # break con
        if cv2.waitKey(1) == ord('q'):
            break

    # cleanup vid
    video_writer.release()
    cap.release()
    cv2.destroyAllWindows()

    audio_frames = audio_frames[:len(audio_frames) // fps * fps]

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


# ffmpeg command to merge audio and vid
def merge_audio_video(output_file, folder_name):
    video_file = os.path.join(folder_name, 'output_video.mp4')
    audio_file = os.path.join(folder_name, 'output_audio.wav')

    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    subprocess.call(command, shell=True)


# work in progress
# TODO only english
# TODO timestaps don't work
def generate_closed_captions(audio_file_path):
    r = sr.Recognizer()

    # Load audio
    with sr.AudioFile(audio_file_path) as source:
        audio = r.record(source)

    captions = []

    try:
        # Perform sr
        text = r.recognize_google(audio)

        # Split the text?
        sentences = text.split(". ")

        # timestamps4later
        timestamp = datetime.datetime.min
        time_increment = datetime.timedelta(seconds=3)  # Adjust as needed

        # ???
        for sentence in sentences:
            start_time = timestamp.strftime("%H:%M:%S.%f")[:-3]
            timestamp += time_increment
            end_time = timestamp.strftime("%H:%M:%S.%f")[:-3]
            caption = f"{start_time} --> {end_time}\n{sentence}"
            captions.append(caption)

    except sr.UnknownValueError:
        print("Speech recognition could not understand audio.")

    return captions


def save_closed_captions(captions, output_file_path):
    with open(output_file_path, "w") as file:
        for i, caption in enumerate(captions, start=1):
            file.write(str(i) + "\n")
            file.write(caption + "\n\n")


def merge_captions_with_video():
    pass

folder_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# save everything in folder
video_output_file = 'output_video.mp4'
audio_output_file = 'output_audio.wav'
output_file_path = "closed_captions.vtt"
audio_file_path = os.path.join(folder_name, audio_output_file)

record_video_audio(video_output_file, audio_output_file, folder_name)
merge_audio_video('merged_output.mp4', folder_name)
captions = generate_closed_captions(audio_file_path)
save_closed_captions(captions, output_file_path)

file_path_merged = os.path.join(os.getcwd(), "merged_output.mp4")
file_path_cc = os.path.join(os.getcwd(), "closed_captions.vtt")
directory_path = os.path.join(os.getcwd(), folder_name)

if not os.path.exists(directory_path):
    os.makedirs(directory_path)

shutil.move(file_path_merged, directory_path)
shutil.move(file_path_cc, directory_path)

# TODO Clean up code
# TODO impl. partition into frames w/  ffmpeg
# TODO MQTT to sync up 4 later
