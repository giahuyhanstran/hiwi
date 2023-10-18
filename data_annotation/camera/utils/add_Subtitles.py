# TODO Speech to Text
import argparse
import os
import speech_recognition as sr
import datetime


def speech_to_text(input_file):
    r = sr.Recognizer()
    file = f"{current_date}.txt"

    with sr.AudioFile(input_file) as source:

        audio = r.listen(source)

        try:
            transcription = (r.recognize_google(audio, language="en-US"))
            with open(file, "w") as output_file:
                output_file.write(transcription)
        except sr.UnknownValueError:
            # handle unrecognized speech - insert a placeholder
            placeholder = "<unrecognized>"
            with open(file, "w") as output_file:
                output_file.write(placeholder)
    return file


# TODO create Closed Caption

def create_closed_caption(speech_to_text_file):
    file = f"{current_date}.txt"
    my_file = open(file, "r")
    data = my_file.read()
    my_file.close()

    return data


def create_word_dictionary(string):
    words = string.split()
    num_entries = len(words) // 7  # Number of complete entries

    word_dict = {}
    for i in range(num_entries):
        start = i * 7
        end = start + 7
        word_dict[i] = ' '.join(words[start:end])

    if len(words) % 7 != 0:
        # If there are remaining words that don't form a complete entry
        word_dict[num_entries] = ' '.join(words[num_entries * 7:])

    return word_dict


def generate_srt(word_dict):
    # 00:00:00
    start_time = datetime.datetime(100, 1, 1, 0, 0, 0)
    print(start_time)

    for key, value in word_dict.items():
        time_add = (len(value.split())) * .5  # .5 sec per word; arbitrarily chosen
        end_time = start_time + datetime.timedelta(0, time_add)

        with open(f'{current_date}.srt', 'a') as f:
            f.write(str(key))
            f.write("\n")
            f.write(start_time.strftime("%H:%M:%S,%f")[:-3])
            f.write(" --> ")
            f.write(end_time.strftime("%H:%M:%S,%f")[:-3])
            f.write("\n")
            f.write(value)
            f.write("\n")
            f.write("\n")

        start_time = end_time + datetime.timedelta(seconds=.5)


# add subtitles with VLC

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='add subtitles')
    parser.add_argument('--current_date', type=str, help='yyyy-mm-dd_hh-mm-ss')
    args = parser.parse_args()
    current_date = args.current_date

    DIRECTORY = os.path.join(os.getcwd(), current_date)
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    os.chdir(DIRECTORY)

    file_path = os.path.join(os.getcwd(), f'{current_date}.wav')

    generate_srt(create_word_dictionary(create_closed_caption(speech_to_text(file_path))))
