import cv2
import pyaudio
import paho.mqtt.client as mqtt
from random import randint
import struct
import uuid
from utils.video_processor import Video_Processor

class RGB_Video_Recorder:
    
    def __init__(self, args):
        self.__args = args
        self.__device_name: str = self.__args.device
        self.__client = None
        self.__hb_interval: int = args.hb_interval
        self.__video_device: int = self.__args.vid_cap
        self.__uuid = uuid.UUID(args.uuid).bytes
        self.__length = self.__args.length
        self.__save_loc = self.__args.save_loc + '/'

        if self.__args.pub_hb:
            self.__client = mqtt.Client(self.__device_name)
            self.__client.connect(host=self.__args.ip, port=self.__args.port)

    def record_video_audio(self):
        cap = cv2.VideoCapture(self.__video_device)

        if cap.isOpened():
            frame_counter = 0
            Done = False

        vp = Video_Processor(save_location = self.__save_loc)

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

            if self.__args.pub_hb and (frame_counter / FPS % self.__hb_interval == 0):
                frame_counter_bytes = struct.pack('!I', frame_counter)
                data = bytearray(frame_counter_bytes + self.__uuid)
                self.__client.publish(f"heartbeat/{self.__device_name}", data)

            vp.write_data(frame, audio_data)
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
        stream.stop_stream()
        stream.close()
        p.terminate()

        vp.stop_writer()
        # vp.merge_audio_video() don't merge rn because of ffmep