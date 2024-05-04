import os
import subprocess
import time

import cv2
from tqdm import tqdm

main_folder = os.getenv("ROOT_FOLDER")


def walk_dirs():
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.endswith(".mp4"):
                video_file = os.path.join(root, file)
                generate_preview_clip(video_file, root)


def generate_preview_clip(video_file: str, output_dir: str, clip_count=10, clip_duration=3,
                          output_resolution=(640, 360)):
    if os.path.exists(os.path.join(output_dir, "preview.mp4")):
        return
    if os.path.exists(os.path.join(output_dir, "0.mp4")):
        return
    print(f"Generating preview for {video_file} to {output_dir}")
    start_time: int = int(time.time())

    frame_rate: int = get_video_frame_rate(video_file)
    video_length: int = get_video_length(video_file)
    hw_accel = os.getenv("HW_ACCEL", "cpu")
    if hw_accel == "qsv":
        video_codec = "h264_qsv"
    elif hw_accel == "amf":
        video_codec = "h264_amf"
    else:
        video_codec = "libx264"
    for i in tqdm(range(clip_count)):
        output_file: str = os.path.join(output_dir, f"{i}.mp4")
        clip_start: int = int(video_length / clip_count * i)
        subprocess.run(
            [
                "ffmpeg", "-i", video_file, "-ss", str(clip_start), "-t", str(clip_duration),
                "-vf", f"scale={output_resolution[0]}:{output_resolution[1]}", "-c:v", video_codec, "-c:a", "aac",
                output_file
            ]
        )

    with open(os.path.join(output_dir, "concat.txt"), "w") as f:
        for i in range(clip_count):
            f.write(f"file '{i}.mp4'\n")

    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", os.path.join(output_dir, "concat.txt"),
         "-c:v", video_codec, "-c:a", "copy", os.path.join(output_dir, "preview.mp4")]
    )
    for i in range(clip_count):
        os.remove(os.path.join(output_dir, f"{i}.mp4"))

    os.remove(os.path.join(output_dir, "concat.txt"))
    end_time: int = int(time.time())
    print(f"Preview generated in {end_time - start_time} seconds")

def get_video_length(video_file: str) -> int:
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return round(frame_count / fps)


def get_video_frame_rate(video_file: str) -> int:
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return round(fps)


if __name__ == "__main__":
    walk_dirs()
