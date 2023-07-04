import os
import subprocess
import argparse


def get_frame_from_file(current_date, timestamp):
    file_path = os.path.join(os.getcwd(), current_date, f'{current_date}_merged.mp4')
    image_path = os.path.join(os.getcwd(), current_date, f'{timestamp}.png')
    command = f'ffmpeg -i {file_path} -vf "select=eq(n\,{timestamp})" -vframes 1 {image_path}'
    subprocess.call(command, shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get frame from mp4')
    parser.add_argument('--frame', type=int)
    parser.add_argument('--current_date', type=str, help='yyyy-mm-dd_hh-mm-ss')
    args = parser.parse_args()

    frame = args.frame
    current_date = args.current_date

    get_frame_from_file(current_date, frame)
