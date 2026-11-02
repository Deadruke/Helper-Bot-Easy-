import os
import yt_dlp


def download_video(url: str, output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
