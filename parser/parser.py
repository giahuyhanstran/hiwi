import json
import os
import re
import argparse
import datetime
import base64

EXAMPLE_DATA = '($sensfloor-event (!EventMillis 1442903959250l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-generic-message (!RawMessage |/QE1AAACp4KnAACAAAE1gAA=|))))'

# python parser.py --sensfloordata '(:event 0 ((!EventMillis 1330330108324l) (!EventType MESSAGE_RECEIVED) (!Message ((!RawMessage |/QE1AQQAAAAtAAAAAAIBAAU=|)))) ($filter/atomic))'

DATA = [

    '($sensfloor-event (!EventMillis 1442903959250l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-generic-message (!RawMessage |/QE1AAACp4KnAACAAAE1gAA=|))))'
    '($sensfloor-event (!EventMillis 1442903960116l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-sensor-change-message (!RawMessage |/QE1BQMAAAHfAAAAJwYAAgA=|))))',
    '($sensfloor-event (!EventMillis 1442903960212l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-sensor-change-message (!RawMessage |/QE1BQMIAAHfAAAAVA0BAwA=|))))',
    '($sensfloor-event (!EventMillis 1442903960328l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-sensor-change-message (!RawMessage |/QE1BQMIAAHfAAAAfRsHAwA=|))))',
    '($sensfloor-event (!EventMillis 1442903960432l) (!EventType ($sensfloor-event-type MESSAGE_RECEIVED)) (!Message ($sensfloor-sensor-change-message (!RawMessage |/QE1BQMIAADfAAAAfhsHAgA=|))))',
]


def extract_msg():
    file_path = 'SensFloor_1442903957972.txt'
    list_of_msg = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                comma_index = line.find(',')
                if comma_index != -1:
                    list_of_msg.append(line[comma_index + 1:].strip())
                else:
                    print("No comma found in this line:", line.strip())
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return list_of_msg


def parse_event_string(event_string):
    result = {}

    event_type_match = re.search(r'\(!EventType \(\$(.*?)\)\)', event_string)
    if event_type_match:
        result['event_type'] = event_type_match.group(1)

    event_match = re.search(r'\(!EventMillis (\d+)l\)', event_string)
    if event_match:
        result['event_millis'] = int(event_match.group(1))

    message_type_match = re.search(r'\(!Message \(\$(.*?) \(', event_string)
    if message_type_match:
        result['message_type'] = message_type_match.group(1)

    message_match = re.search(r'\(!RawMessage \|(.*?)\|\)', event_string)
    if message_match:
        result['raw_message'] = message_match.group(1)

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


def decode_message(byte_list, result):

    msg_byte_list = byte_list[1:9]
    data_byte_list = byte_list[9:17]

    # fd indicates Message
    if not (byte_list[0] == 'fd'):
        raise ValueError('invalid Message')

    else:
        # MESSAGE 00-07

        # Group Identification
        # every room has unique GID
        result['GID'] = ''.join(msg_byte_list[0:2])


        # MODIDS coordinate x/y (XX YY) X and Y Int
        # MODIDR if e.g. XXYY = 01FF then enum from 0100 to 01FF
        result['MODID'] = ''.join(msg_byte_list[2:4])

        # Bit0 first Sensor Bit 1 second etc
        # if SENS = 12 => 0010010 (Bit 1 and Bit 4)
        result['SENS'] = msg_byte_list[4]

        # Temperature at Location of Module (In Celsius)
        # Temp = .24*T - 297, T = 256*THIGH + TLOW
        result['THIGH'] = msg_byte_list[5]

        # defines meaning of message
        # eg 01: Sensor State cahnged, 02: Beacon signal
        result['DEF'] = msg_byte_list[6]

        # defines Parameter for DEF
        # eg: DEF=10: LED blinking mode and Para==0 or 01 is OFF and ON
        result['PARA'] = msg_byte_list[7]

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
        for index, value in enumerate(data_byte_list):
            result[f'byte{index}'] = data_byte_list[index]



        # TODO content length varies depending on PARA

        return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='optional String input')
    parser.add_argument('--sensfloordata', type=str, help='data key value')
    args = parser.parse_args()

    sensfloordata = args.sensfloordata if args.sensfloordata is not None else EXAMPLE_DATA

    # parsed_data = parse_event_string(sensfloordata)
    for data in extract_msg():


        decoded_data = decode_message(decode_base64_to_hex_list(parse_event_string(data)),
                                      (parse_event_string(data)))
        #print(decoded_data)
        if not (decoded_data['DEF'] == '01'):
            continue
        else:

            date = decoded_data['event_millis']

            # with open(os.path.join(os.getcwd(), 'json_folder', f"parsed_data_{current_time}.json"), 'w') as js:
            #    json.dump(parsed_data, js, indent=4)
            with open(os.path.join(os.getcwd(), 'json_folder', f"decoded_data_{date}.json"), 'w') as js:
                json.dump(decoded_data, js, indent=1)
