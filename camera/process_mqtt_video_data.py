from utils.video_processor import Video_Processor


def main():
    vp = Video_Processor()
    vp.receive_mqtt_messages()
    vp.merge_audio_video()

if __name__ == '__main__':
    main()