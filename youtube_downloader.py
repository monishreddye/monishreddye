#!/usr/bin/env python3
"""Download a YouTube video at the highest available quality.

The script prompts you to paste a YouTube link (or you can pass it as a
command-line argument). It then inspects the available formats, selects the
best video and best audio streams, downloads them, and merges them into a
single file on your local drive using ffmpeg.

Usage:
    python youtube_downloader.py
    python youtube_downloader.py "https://www.youtube.com/watch?v=XXXXXXXXXXX"
    python youtube_downloader.py "<link>" --output ~/Videos
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:
    sys.exit(
        "The 'yt-dlp' package is required.\n"
        "Install it with:  pip install -r requirements.txt\n"
        "or:               pip install yt-dlp"
    )


def _human_readable_size(num_bytes):
    """Return a nicely formatted file size string."""
    if not num_bytes:
        return "unknown size"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def _progress_hook(status):
    """Print a simple, single-line progress indicator."""
    if status["status"] == "downloading":
        percent = status.get("_percent_str", "").strip()
        speed = status.get("_speed_str", "").strip()
        eta = status.get("_eta_str", "").strip()
        sys.stdout.write(f"\rDownloading... {percent} at {speed} (ETA {eta})   ")
        sys.stdout.flush()
    elif status["status"] == "finished":
        sys.stdout.write("\rDownload complete. Merging/processing...          \n")
        sys.stdout.flush()


def get_link_from_user():
    """Prompt the user to paste a YouTube link."""
    try:
        link = input("Paste the YouTube video link and press Enter: ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit("\nNo link provided. Exiting.")
    if not link:
        sys.exit("No link provided. Exiting.")
    return link


def download_video(url, output_dir):
    """Download the highest quality version of the given YouTube video.

    Selects the best available video stream combined with the best audio
    stream. If ffmpeg is available they are merged into a single MP4 file;
    otherwise yt-dlp falls back to the best single pre-merged file.
    """
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_available = shutil.which("ffmpeg") is not None
    if not ffmpeg_available:
        print(
            "Warning: ffmpeg was not found on your system. YouTube serves the "
            "highest resolutions as separate video/audio streams that must be "
            "merged with ffmpeg.\nWithout it, the best *combined* stream will be "
            "downloaded instead (this may be a lower resolution).\n"
            "Install ffmpeg from https://ffmpeg.org/download.html for full quality.\n"
        )

    if ffmpeg_available:
        # Best video + best audio, merged. Falls back to best combined stream.
        format_selector = "bestvideo*+bestaudio/best"
    else:
        format_selector = "best"

    ydl_opts = {
        "format": format_selector,
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
        "progress_hooks": [_progress_hook],
        "noplaylist": True,
        "restrictfilenames": False,
        "ignoreerrors": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        # First, fetch metadata so we can show the user what will be downloaded.
        info = ydl.extract_info(url, download=False)

        title = info.get("title", "Unknown title")
        uploader = info.get("uploader", "Unknown uploader")
        duration = info.get("duration")
        print("\n" + "=" * 60)
        print(f"Title    : {title}")
        print(f"Channel  : {uploader}")
        if duration:
            minutes, seconds = divmod(int(duration), 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                print(f"Duration : {hours}h {minutes}m {seconds}s")
            else:
                print(f"Duration : {minutes}m {seconds}s")

        # Report the resolution that will actually be downloaded.
        requested = info.get("requested_formats")
        if requested:
            heights = [f.get("height") for f in requested if f.get("height")]
            if heights:
                print(f"Quality  : {max(heights)}p (highest available)")
        elif info.get("height"):
            print(f"Quality  : {info['height']}p (best combined stream)")
        print("=" * 60 + "\n")

        # Now perform the actual download.
        ydl.download([url])

    print(f"\nSaved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube video at the highest available quality."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="YouTube video link. If omitted, you will be prompted to paste one.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Directory to save the video (default: ./downloads).",
    )
    args = parser.parse_args()

    url = args.url or get_link_from_user()

    try:
        download_video(url, args.output)
    except DownloadError as exc:
        sys.exit(f"\nDownload failed: {exc}")
    except KeyboardInterrupt:
        sys.exit("\nDownload cancelled by user.")


if __name__ == "__main__":
    main()
