import json
import os
import re
import argparse
import datetime
import base64

EXAMPLE_DATA = '(:event 0 ((!EventMillis 1330330108324l) (!EventType MESSAGE_RECEIVED) (!Message ((!RawMessage |/QE1AQQAAAAtAAAAAAIBAAU=|)))) ($filter/atomic))'

# python parser.py --sensfloordata '(:event 0 ((!EventMillis 1330330108324l) (!EventType MESSAGE_RECEIVED) (!Message ((!RawMessage |/QE1AQQAAAAtAAAAAAIBAAU=|)))) ($filter/atomic))'


def parse_event_string(event_string):
    result = {}

    event_match = re.match(r'\(:event (\d+) \(\(!EventMillis (\d+)l\) \(!EventType (\w+)\)', event_string)
    if event_match:
        result['event_number'] = int(event_match.group(1))
        result['event_millis'] = int(event_match.group(2))
        result['event_type'] = event_match.group(3)

    message_match = re.search(r'(!Message \(\(!RawMessage \|(.*?)\|\)\)\))', event_string)
    if message_match:
        result['raw_message'] = message_match.group(2)

    filter_match = re.search(r'\(\$filter/(.*?)\)', event_string)
    if filter_match:
        result['filter'] = filter_match.group(1)

    return result


def decode_base64_to_hex_list(result):
    base64_msg = result['raw_message'].encode('ascii')

    decoded = base64.decodebytes(base64_msg).hex()
    hex_list = []

    for i in range(1, int(len(decoded) / 2) + 1):
        hex_list.append(decoded[(i - 1) * 2:2 * i])
        i += 2

    return hex_list


def decode_message(byte_list):
    msg_byte_list = byte_list[1:9]
    data_byte_list = byte_list[9:17]
    msg_format = {}

    # fd indicates Message
    if not (byte_list[0] == 'fd'):
        raise ValueError('invade Message')

    else:
        # MESSAGE 00-07

        # Group Identification
        # every room has unique GID
        msg_format['GID'] = ''.join(msg_byte_list[0:2])

        # MODIDS coordinate x/y (XX YY) X and Y Int
        # MODIDR if e.g. XXYY = 01FF then enum from 0100 to 01FF
        msg_format['MODID'] = ''.join(msg_byte_list[2:4])

        # Bit0 first Sensor Bit 1 second etc
        # if SENS = 12 => 0010010 (Bit 1 and Bit 4)
        msg_format['SENS'] = ''.join(msg_byte_list[4])

        # Temperature at Location of Module (In Celsius)
        # Temp = .24*T - 297, T = 256*THIGH + TLOW
        msg_format['THIGH'] = ''.join(msg_byte_list[5])

        # defines meaning of message
        # eg 01: Sensor State cahnged, 02: Beacon signal
        msg_format['DEF'] = ''.join(msg_byte_list[6])

        # defines Parameter for DEF
        # eg: DEF=10: LED blinking mode and Para==0 or 01 is OFF and ON
        msg_format['PARA'] = ''.join(msg_byte_list[7])

        # DATA 08-15
        '''
        The blocks (denominated by PARA) have varying contents
        Each block has 8 bytes (DATA) assigned to it
        There are a total of 10 blocks (0-9)
        Blocks 0-3 are read only
        BLocks 4-9 contain parameters that can be changed by user
        BLocks 0A(10)-7F(127) can store arbitrary data
        Read the friendly manual for further information
        '''
        # TODO content length varies depending on PARA
        for index, value in enumerate(data_byte_list):
            msg_format[f'Byte{index}'] = data_byte_list[index]

        return msg_format


if __name__ == '__main__':
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    parser = argparse.ArgumentParser(description='optional String input')
    parser.add_argument('--sensfloordata', type=str, help='data key value')
    args = parser.parse_args()

    sensfloordata = args.sensfloordata if args.sensfloordata is not None else EXAMPLE_DATA

    parsed_data = parse_event_string(sensfloordata)
    decded_data = decode_message(decode_base64_to_hex_list(parse_event_string(sensfloordata)))

    with open(os.path.join(os.getcwd(), 'json_folder', f"parsed_data_{current_time}.json"), 'w') as js:
        json.dump(parsed_data, js, indent=4)
    with open(os.path.join(os.getcwd(), 'json_folder', f"encoded_data_{current_time}.json"), 'w') as js:
        json.dump(decded_data, js, indent=1)
