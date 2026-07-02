#!/usr/bin/env python3
"""Download a YouTube video at the highest available quality.

The script asks the user to enter (or paste) a YouTube link, inspects the
available formats, picks the best video + best audio streams, and saves the
merged file to a local folder.

Usage:
    python youtube_downloader.py                 # prompts for a link
    python youtube_downloader.py <youtube-url>   # link passed as an argument

Requirements:
    pip install -r requirements.txt

    ffmpeg must be installed and on PATH to merge the best video and audio
    streams into a single file. If ffmpeg is missing, the script falls back
    to the best single (pre-merged) format YouTube offers.
"""

import shutil
import sys
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

DOWNLOAD_DIR = Path.home() / "Downloads" / "YouTube"


def get_link() -> str:
    """Read the YouTube link from the command line or an interactive prompt."""
    if len(sys.argv) > 1:
        return sys.argv[1].strip()

    link = input("Enter or paste the YouTube link: ").strip()
    if not link:
        print("No link entered. Exiting.")
        sys.exit(1)
    return link


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def build_options(merge_streams: bool) -> dict:
    """Build yt-dlp options that select the highest quality available."""
    if merge_streams:
        # Best video-only stream + best audio-only stream, merged via ffmpeg.
        # Falls back to the best combined stream if separate ones don't exist.
        fmt = "bestvideo+bestaudio/best"
    else:
        # Without ffmpeg we can only take the best pre-merged stream.
        fmt = "best"

    return {
        "format": fmt,
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [progress_hook],
    }


def progress_hook(status: dict) -> None:
    if status["status"] == "downloading":
        percent = status.get("_percent_str", "").strip()
        speed = status.get("_speed_str", "").strip()
        eta = status.get("_eta_str", "").strip()
        print(f"\rDownloading... {percent} at {speed} (ETA {eta})   ", end="")
    elif status["status"] == "finished":
        print(f"\nDownload finished: {status.get('filename', '')}")


def download(link: str) -> None:
    merge = ffmpeg_available()
    if not merge:
        print(
            "Warning: ffmpeg was not found on your system. "
            "Downloading the best pre-merged quality instead of the absolute "
            "highest. Install ffmpeg to get the maximum resolution."
        )

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    options = build_options(merge)

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(link, download=False)
        title = info.get("title", "Unknown title")
        height = info.get("height")
        fps = info.get("fps")
        quality = f"{height}p" if height else "best available"
        if fps:
            quality += f" @ {fps:.0f}fps"

        print(f"\nTitle:   {title}")
        print(f"Quality: {quality} (highest available)")
        print(f"Saving to: {DOWNLOAD_DIR}\n")

        ydl.download([link])

    print("\nDone! The video (with audio) has been saved to your local drive.")


def main() -> None:
    link = get_link()
    try:
        download(link)
    except DownloadError as exc:
        print(f"\nDownload failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
