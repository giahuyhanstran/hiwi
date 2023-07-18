import argparse
import cv2
import pyaudio
import pickle
import paho.mqtt.client as mqtt
from random import randint
import struct
import uuid

# TODO (if not arg.pub_data) -> save data locally, avoid data chunks and all that


class RGB_Video_Recorder:
    
    def __init__(self, args, cfg):
        self.__cfg = cfg
        self.__args = args
        self.__device_name: str = self.__cfg['CAMERA']['DEVICE_NAME']
        self.__client = None
        self.__hb_interval: int = args.hb_interval
        self.__video_device: int = self.__cfg['CAMERA']['VIDEO_DEVICE']
        self.__uuid = uuid.UUID(self.__cfg['CAMERA']['UUID']).bytes
        self.__length = self.__args.length if self.__args.length is not None else None

        if self.__args.pub_hb or args.pub_data:
            self.__client = mqtt.Client('RGB_Test_Camera' + '_' + str(randint(1, 1000000)))
            self.__client.connect(host=self.__cfg['MQTT']['ADDRESS'], port=self.__cfg['MQTT']['PORT'])


    def __record_video_audio(self):
        cap = cv2.VideoCapture(self.__video_device)

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

            if self.__args.pub_hb and (frame_counter / FPS % self.__hb_interval == 0):
                frame_counter_bytes = struct.pack('!I', frame_counter)
                data = bytearray(frame_counter_bytes + self.__uuid)
                self.__client.publish(f"heartbeat/{self.__device_name}", data)

            if self.__args.pub_data:
                self.__client.publish("Camera", pickle.dumps(video_data))
            else:
                pass # save data locally

            cv2.imshow("Camera", frame)

            frame_counter += 1
            

            if self.__length is not None:
                if frame_counter/FPS >= self.__length:
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