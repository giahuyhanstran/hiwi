# work in progress
# TODO only english
# TODO timestaps don't work
def generate_closed_captions(audio_file_path):
    r = sr.Recognizer()

    # Load audio
    with sr.AudioFile(audio_file_path) as source:
        audio = r.record(source)

    captions = []

    try:
        # Perform sr
        text = r.recognize_google(audio)

        # Split the text?
        sentences = text.split(". ")

        # timestamps4later
        timestamp = datetime.datetime.min
        time_increment = datetime.timedelta(seconds=3)  # Adjust as needed

        # ???
        for sentence in sentences:
            start_time = timestamp.strftime("%H:%M:%S.%f")[:-3]
            timestamp += time_increment
            end_time = timestamp.strftime("%H:%M:%S.%f")[:-3]
            caption = f"{start_time} --> {end_time}\n{sentence}"
            captions.append(caption)

    except sr.UnknownValueError:
        print("Speech recognition could not understand audio.")

    return captions


def save_closed_captions(captions, output_file_path):
    with open(output_file_path, "w") as file:
        for i, caption in enumerate(captions, start=1):
            file.write(str(i) + "\n")
            file.write(caption + "\n\n")


def merge_captions_with_video():
    pass


captions = generate_closed_captions(audio_file_path)
save_closed_captions(captions, output_file_path)

shutil.move(file_path_cc, directory_path)
file_path_cc = os.path.join(os.getcwd(), "closed_captions.vtt")
output_file_path = "closed_captions.vtt"