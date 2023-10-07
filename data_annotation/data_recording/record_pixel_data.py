import os
import yaml
from utils.mqtt_subscriber import MQTTSubscriber
import argparse

current_dir = os.path.dirname(os.path.abspath(__file__))


def _get_config(filename: str ='config.yml') -> dict:
    ''' Method to load data out of config file

    Args:
        filename: Name of the config file to be loaded.

    Returns:
        A dict with all data from the config file.
    '''
    if filename == 'config.yml':
        cfg_file = os.path.join(current_dir, filename)
    else:
        cfg_file = fr'{filename}'
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"""{filename} not found. 
                                Please use the command: 
                                '--cfg <path to your config.yml> -h' 
                                to get further information.""")
    with open(cfg_file) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    assert cfg['READ_FROM'] in ['BLE', 'MQTT'], 'invalid READ_FROM value'

    return cfg

def fill_choices(cfg):
    sensor_mac = []
    names = []
    for zone, zone_info in cfg.items():
        if "ZONE" in zone and "MAC_ADDRESS" in zone_info:
            sensor_mac.append(zone_info["MAC_ADDRESS"])
            if "NAME" in zone_info:
                names.append(zone_info["NAME"])
    return sensor_mac + names

def main():

    parser_cfg = argparse.ArgumentParser(add_help= False, description=
                                         '''Provide path to a specific config.yml for data recording.
                                         Default: Looks for `config.yml` in current working directory.''')
    
    parser_cfg.add_argument('--cfg', type=str, default='config.yml', 
                            help='''Expects the full path to the config.yml file. 
                                 Default: Looks for `config.yml` in current working directory.''')
    
    arg, unknown_args = parser_cfg.parse_known_args()   

    cfg = _get_config(arg.cfg)
    choices = fill_choices(cfg)
    type_choices = list(map(str.lower, cfg['READING'].keys()))

    # Get all choices for include and exclude arguments
    parser = argparse.ArgumentParser(parents=[parser_cfg], description= 
                                     '''The arguments filter what you are interested in from the available data. 
                                     Your choices are retrieved from the config.yml file. 
                                     Default: Don't pass args and get everything. 
                                     Note: The include argument is prioritised over the exclude argument, 
                                     meaning the same value in both arguments includes the data.''')
    
    parser.add_argument('--include', type=str, nargs='*', 
                        choices=choices, default=None, 
                        help='Defines of what sensor units you do want to receive data. Choose between MAC or Name.')
    
    parser.add_argument('--exclude', type=str, nargs='*', 
                        choices=choices, default=None, 
                        help='Defines of what sensor units you do NOT want to receive data. Choose between MAC or Name.')
    
    parser.add_argument('--type', type=str, choices=type_choices, 
                        help='What kind of data you want to receive, of the selected sensor units.')

    args = parser.parse_args(unknown_args)

    receiver = MQTTSubscriber(cfg, args)
    receiver.receive_messages()

if __name__ == '__main__':
    main()
