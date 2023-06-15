import json
import os
import re
import argparse
import datetime

EXAMPLE_DATA = '(:event 0 ((!EventMillis 1330330108324l) (!EventType MESSAGE_RECEIVED) (!Message ((!RawMessage |/QE1AQQAAAAtAAAAAAIBAAU=|)))) ($filter/atomic))'


# python parser.py --sensfloordata '(:event 0 ((!EventMillis 1330330108324l) (!EventType MESSAGE_RECEIVED) (!Message ((!RawMessage |/QE1AQQAAAAtAAAAAAIBAAU=|)))) ($filter/atomic))'

def parse_event_string(event_string):
    result = {}

    event_match = re.match(r'\(:event (\d+) \(\(!EventMillis (\d+)l\) \(!EventType (\w+)\)', event_string)
    if event_match:
        result['event_number'] = int(event_match.group(1))
        result['event_millis'] = int(event_match.group(2))
        result['event_type'] = event_match.group(3)

    message_match = re.search(r'(!Message \(\(!RawMessage (.*?)\)\)\))', event_string)
    if message_match:
        result['raw_message'] = message_match.group(2)

    filter_match = re.search(r'\(\$filter/(.*?)\)', event_string)
    if filter_match:
        result['filter'] = filter_match.group(1)

    return result


if __name__ == '__main__':
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    parser = argparse.ArgumentParser(description='optional String input')
    parser.add_argument('--sensfloordata', type=str, help='data key value')
    args = parser.parse_args()

    sensfloordata = args.sensfloordata if args.sensfloordata is not None else EXAMPLE_DATA

    parsed_data = parse_event_string(sensfloordata)

    with open(os.path.join('.', '/home/huy/work/parser/json_folder/', f"parsed_data_{current_time}.json"), 'w') as js:
        json.dump(parsed_data, js, indent=4)
