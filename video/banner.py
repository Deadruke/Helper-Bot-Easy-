import subprocess


def add_text_banner(
    input_path: str,
    output_path: str,
    text: str = "МОЙ КЛИП",
    position: str = "bottom"
):
    y_position = (
        "h-th-80" if position == "bottom" else "40"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf",
        (
            f"drawtext=text='{text}':"
            "fontcolor=white:"
            "fontsize=42:"
            "box=1:"
            "boxcolor=black@0.65:"
            "boxborderw=18:"
            f"x=(w-text_w)/2:y={y_position}"
        ),
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
