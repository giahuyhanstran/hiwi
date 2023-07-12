import argparse
import cv2
import pyaudio
import pickle
import paho.mqtt.client as mqtt
import ast

'''
Note: Script is publishing on localhost port 1883 for topic "Camera"
      At first start HiveMQ Broker, then run this script, then
      run process_video.py. You can use MQTT Explorer to check for data traffic.
'''


# TODO (if not arg.pub_data) -> save data locally, avoid data chunks and all that


def record_video_audio():
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        frame_counter = 0
        Done = False

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

        if args.pub_hb and (frame_counter / FPS % heartbeat_interval_seconds == 0):
            client.publish("Heartbeat", frame_counter)

        if args.pub_data:
            client.publish("Camera", pickle.dumps(video_data))
        else:
            pass # save data locally

        cv2.imshow("Camera", frame)

        frame_counter += 1
        

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

    parser = argparse.ArgumentParser()
    parser.add_argument('--length', type=int, help='default until interrupt, else time in seconds')
    parser.add_argument('--hb_interval', type=int, help='heartbeat interval in seconds, default = 1', default=1)
    parser.add_argument('--pub_hb', type=ast.literal_eval, help='publish heartbeat? True or False, default = True', default=True)
    parser.add_argument('--pub_data', type=ast.literal_eval, help='publish data? True or False, else save locally, default = True', default=True)
    args = parser.parse_args()

    heartbeat_interval_seconds = args.hb_interval

    length = args.length if args.length is not None else None

    if not args.pub_hb and not args.pub_data:
        # Define MQTT Client and address of broker
        mqttBroker = '192.168.1.80'
        # mqttBroker_L = "localhost"
        client = mqtt.Client("camera data")
        client.connect(host=mqttBroker, port=1883)

    record_video_audio()
