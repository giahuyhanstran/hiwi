import cv2
import pyaudio
import pickle
import paho.mqtt.client as mqtt

'''
Note: Script is publishing on localhost port 1883 for topic "Camera"
      At first start HiveMQ Broker, then run this script, then
      run process_video.py. You can use MQTT Explorer to check for data traffic.
'''

def record_video_audio():
    cap = cv2.VideoCapture(0)

    # default settings
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    audio_format = pyaudio.paInt16
    audio_channels = 2
    audio_sample_rate = 44100
    audio_chunk_size = int(audio_sample_rate / fps)

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format,
                    channels=audio_channels,
                    rate=audio_sample_rate,
                    input=True,
                    frames_per_buffer=audio_chunk_size)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        audio_data = stream.read(audio_chunk_size)
        video_data = (frame, audio_data)

        # Publish video_data as an MQTT message
        client.publish("Camera", pickle.dumps(video_data))

        cv2.imshow("Camera", frame)

        # break condition
        if cv2.waitKey(1) == ord('q'):
            break

    # cleanup
    cap.release()
    cv2.destroyAllWindows()

    # clean up audio
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':

    # Define MQTT Client and address of broker
    mqttBroker = "localhost"
    client = mqtt.Client("camera data")
    client.connect(host=mqttBroker, port=1883)
    
    record_video_audio()