import os
import yaml
from utils.mqqt_subscriber import MQTTSubscriber

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


def main():
    '''Main method'''

    # get the config
    cfg = _get_config()
    # initialize MQTT subscriber
    receiver = MQTTSubscriber(cfg)
    # receive messages
    receiver.receive_messages()


if __name__ == '__main__':
    main()
