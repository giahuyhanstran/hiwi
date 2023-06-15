import cv2
import datetime
import argparse
import os

# python camera.py --fps 30 --recording-time 10

HEIGHT = 480
WIDTH = 640
DEFAULT_FPS = 30.0
DEFAULT_RECORDING_TIME_SECONDS = 5


def video(height, width, frames, folder):
    frame_count = 0
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(folder, current_time)
    os.makedirs(folder_path, exist_ok=True)
    video_name = os.path.join(folder_path, f"{current_time}_Video.mp4")
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*"mp4v"), frames, (width, height))
    return frame_count, out, folder_path


def record_video(fps=DEFAULT_FPS, recording_time=DEFAULT_RECORDING_TIME_SECONDS, output_folder="recordings"):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("unable to load cam")
        return

    frame_count, out, folder_path = video(HEIGHT, WIDTH, fps, output_folder)

    total_frames = int(recording_time * fps)
    start_time = datetime.datetime.now()

    while cap.isOpened() and frame_count < total_frames:
        ret, frame = cap.read()

        if not ret:
            print("no capture frame")
            break

        frame_count += 1

        frame_name = os.path.join(folder_path, f"{datetime.datetime.now()}__frame_{frame_count}.png")
        cv2.imwrite(frame_name, frame)

        out.write(frame)

        cv2.imshow("Camera", frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record video from camera')
    parser.add_argument('--fps', type=float, help='fps default 30.0')
    parser.add_argument('--recording-time', type=int, help='recording time in sec default 30')
    args = parser.parse_args()

    fps = args.fps if args.fps is not None else DEFAULT_FPS
    recording_time = args.recording_time if args.recording_time is not None else DEFAULT_RECORDING_TIME_SECONDS

    record_video(fps, recording_time)

