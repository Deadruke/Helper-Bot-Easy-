import subprocess


def add_subtitles(input_path: str, srt_path: str, output_path: str):
    subtitle_path = srt_path.replace("\\", "/")
    subtitle_path = subtitle_path.replace(":", r"\:")
    subtitle_path = subtitle_path.replace("'", r"\'")

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", f"subtitles='{subtitle_path}'",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "copy",
        output_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])

    return output_path
