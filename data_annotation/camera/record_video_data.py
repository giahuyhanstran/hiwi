import argparse
import ast
from utils.rgb_video_recorder import RGB_Video_Recorder
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--length', type=int, default=None, 
                        help='default until interrupt, else time in seconds')
    parser.add_argument('--hb_interval', type=int, default=1, 
                        help='heartbeat interval in seconds, default = 1')
    parser.add_argument('--pub_hb', type=ast.literal_eval, default=True, 
                        help='publish heartbeat? True or False, default = True')
    parser.add_argument('--device', type=str, default='NoName', 
                        help='Provide a name for the camera_device, default = NoName')
    parser.add_argument('--vid_cap', type=int, default=0, 
                        help='Decide which Video Capture channel open-cv should use, default = 0')
    parser.add_argument('--uuid', type=str, default='70d207b2-d813-4a02-8074-6ba4ad77bdfe', 
                        help='Decide which Video Capture channel open-cv should use, default = 70d207b2-d813-4a02-8074-6ba4ad77bdfe')
    parser.add_argument('--ip', type=str, default='localhost', 
                        help='Pass an ip-address used by the mqtt-Broker to publish heartbeats, default = localhost')
    parser.add_argument('--port', type=int, default=1883, 
                        help='Pass a port used by the mqtt-Broker to publish heartbeats, default = 1883')
    parser.add_argument('--save_loc', type=str, default=None, 
                        help='Enter a path to a folder that will be used as a save location for the recordings, default = None')

    args = parser.parse_args()
    recorder = RGB_Video_Recorder(args)
    recorder.record_video_audio()

if __name__ == '__main__':

    main()