import argparse
import ast
from utils.rgb_video_recorder import RGB_Video_Recorder
import yaml
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def _get_config(filename: str ='rgb_config.yml') -> dict:
    ''' Method to load data out of config file

    Args:
        filename: Name of the config file to be loaded.

    Returns:
        A dict with all data from the config file.
    '''
    if filename == 'rgb_config.yml':
        cfg_file = os.path.join(current_dir, filename)
    else:
        cfg_file = fr'{filename}'
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"""{filename} not found. 
                                Please use the command: 
                                '--cfg <path to your rgb_config.yml> -h' 
                                to get further information.""")
    with open(cfg_file) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)


    return cfg


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--length', type=int, help='default until interrupt, else time in seconds', default=None)
    parser.add_argument('--hb_interval', type=int, help='heartbeat interval in seconds, default = 1', default=1)
    parser.add_argument('--pub_hb', type=ast.literal_eval, help='publish heartbeat? True or False, default = True', default=True)
    parser.add_argument('--pub_data', type=ast.literal_eval, help='publish data? True or False, else save locally, default = True', default=True)
    parser.add_argument('--vid_cap', type=int, help='Decide which Video Capture channel open-cv should use, default = 0', default=0)
    parser.add_argument('--ip', type=str, help='Pass an ip-address used by the mqtt-Broker to publish heartbeats, default = localhost', default='localhost')
    parser.add_argument('--port', type=int, help='Pass a port used by the mqtt-Broker to publish heartbeats, default = 1883', default=1883)
    
    args = parser.parse_args()

    rgb_cfg = _get_config()

    recorder = RGB_Video_Recorder(args, rgb_cfg)
    recorder.record_video_audio()


if __name__ == '__main__':

    main()