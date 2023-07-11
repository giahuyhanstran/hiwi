import argparse

import cv2
import pyaudio
import pickle
import paho.mqtt.client as mqtt

'''
Note: Script is publishing on localhost port 1883 for topic "Camera"
      At first start HiveMQ Broker, then run this script, then
      run process_video.py. You can use MQTT Explorer to check for data traffic.
'''


# TODO optional argsparse for length (mins)
# TODO Optional publishen, optional Heartbeat (frame counter) auf einem extra topic senden
# TODO wie oft wird der heartbeat gesendet

def record_video_audio():
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        frame_counter = 0

    # default settings
    FPS = int(cap.get(cv2.CAP_PROP_FPS))
    AUDIO_FORMAT = pyaudio.paInt16
    AUDIO_CHANNEL = 2
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHUNK_SIZE = int(AUDIO_SAMPLE_RATE / FPS)

    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT,
                    channels=AUDIO_CHANNEL,
                    rate=AUDIO_SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=AUDIO_CHUNK_SIZE)

    while cap.isOpened():

        ret, frame = cap.read()
        if not ret:
            break

        audio_data = stream.read(AUDIO_CHUNK_SIZE)
        video_data = (frame, audio_data)

        client.publish("Camera", pickle.dumps(video_data))

        cv2.imshow("Camera", frame)

        frame_counter += 1
        Done = False

        if length is not None:
            if frame_counter/FPS >= length:
                Done = True

        # break condition
        if cv2.waitKey(1) == ord('q') or Done:
            break

    # cleanup
    cap.release()
    cv2.destroyAllWindows()

    # clean up audio
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get frame from mp4')
    parser.add_argument('--length', type=int, help='default until interrupt, else time in seconds')
    args = parser.parse_args()

    length = args.length if args.length is not None else None

    # Define MQTT Client and address of broker
    mqttBroker = "localhost"
    client = mqtt.Client("camera data")
    client.connect(host=mqttBroker, port=1883)

    record_video_audio()
