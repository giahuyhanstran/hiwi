import os
import yaml
from utils.mqqt_subscriber import MQTTSubscriber
import argparse

current_dir = os.path.dirname(os.path.abspath(__file__))


def _get_config(filename='config.yml') -> dict:
    ''' Method to load data out of config file

    Args:
        filename: Name of the config file to be loaded.

    Returns:
        A dict with all data from the config file.
    '''
    cfg_file = os.path.join(current_dir, filename)
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f'{filename} not found')
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
    
    cfg = _get_config()
    choices = fill_choices(cfg)

    # Get all choices for include and exclude arguments
    parser = argparse.ArgumentParser(description= "include: Get only that data, exclude: Get everything else, type: Select the data type of interest, default: Don't pass args and get everything.")
    parser.add_argument('--include', type=str, nargs='+', choices=choices, default=None, help='Of what sensor units you do want to receive data. Choose between Mac or Name.')
    parser.add_argument('--exclude', type=str, nargs='+', choices=choices, default=None, help='Of what sensor units you do not want to receive data. Choose between Mac or Name.')
    parser.add_argument('--type', type=str, choices=['tof', 'thermal'], help='What kind of data you want to receive of the selected sensor units.')
    args = parser.parse_args()

    receiver = MQTTSubscriber(cfg, args)
    receiver.receive_messages()

if __name__ == '__main__':
    main()
