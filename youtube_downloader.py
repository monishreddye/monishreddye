#!/usr/bin/env python3
"""
YouTube Video Downloader
=========================

Downloads a YouTube video (highest available video quality + best audio,
merged into a single file) to your local drive.

Usage
-----
Interactive (prompts you to paste the link):
    python youtube_downloader.py

Non-interactive:
    python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
    python youtube_downloader.py "https://youtu.be/VIDEO_ID" -o ~/Videos

Requirements
------------
- Python 3.8+
- yt-dlp (see requirements.txt): pip install -r requirements.txt
- ffmpeg installed and available on PATH (needed to merge separate
  video-only and audio-only streams into one file at the highest quality).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:
    print(
        "The 'yt-dlp' package is required but not installed.\n"
        "Install it with:  pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/.+",
    re.IGNORECASE,
)

DEFAULT_OUTPUT_DIR = "downloads"


def is_valid_youtube_url(url: str) -> bool:
    """Basic sanity check that the given string looks like a YouTube URL."""
    return bool(url) and bool(YOUTUBE_URL_PATTERN.match(url.strip()))


def prompt_for_url() -> str:
    """Keep asking the user until a valid-looking YouTube URL is entered."""
    while True:
        url = input("Paste the YouTube video link: ").strip()
        if is_valid_youtube_url(url):
            return url
        print("That doesn't look like a valid YouTube URL. Please try again.\n")


def progress_hook(status: dict) -> None:
    """Print a simple live progress line while the download is in progress."""
    if status["status"] == "downloading":
        percent = status.get("_percent_str", "").strip()
        speed = status.get("_speed_str", "").strip()
        eta = status.get("_eta_str", "").strip()
        filename = Path(status.get("filename", "")).name
        print(f"\rDownloading {filename}: {percent} at {speed}, ETA {eta}   ", end="", flush=True)
    elif status["status"] == "finished":
        print("\nDownload finished, merging/post-processing (if needed)...")


def build_ydl_options(output_dir: str) -> dict:
    """
    Build yt-dlp options that:
      - pick the best available video quality
      - pick the best available audio quality
      - merge them into a single mp4 file (requires ffmpeg)
      - fall back gracefully if a pre-merged 'best' format is the only option
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    return {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(Path(output_dir) / "%(title)s [%(resolution)s].%(ext)s"),
        "restrictfilenames": False,
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
    }


def download_video(url: str, output_dir: str = DEFAULT_OUTPUT_DIR) -> str | None:
    """
    Download the given YouTube URL at the highest available quality.

    Returns the path to the downloaded file on success, or None on failure.
    """
    ydl_opts = build_ydl_options(output_dir)

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except DownloadError as exc:
            print(f"\nCould not access this video: {exc}", file=sys.stderr)
            return None

        title = info.get("title", "video")
        best_height = _best_available_height(info)
        print(f"\nTitle:  {title}")
        if best_height:
            print(f"Best available quality: {best_height}p")
        print(f"Saving to: {Path(output_dir).resolve()}\n")

        try:
            ydl.download([url])
        except DownloadError as exc:
            print(f"\nDownload failed: {exc}", file=sys.stderr)
            return None

        # Re-extract to resolve the final on-disk filename after merging.
        result = ydl.extract_info(url, download=False)
        filepath = ydl.prepare_filename(result)
        merged_path = str(Path(filepath).with_suffix(".mp4"))
        final_path = merged_path if Path(merged_path).exists() else filepath

        return final_path


def _best_available_height(info: dict) -> int | None:
    """Inspect the format list returned by yt-dlp to report the best resolution."""
    formats = info.get("formats") or []
    heights = [f.get("height") for f in formats if f.get("height")]
    return max(heights) if heights else info.get("height")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a YouTube video at the highest available quality."
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="YouTube video URL. If omitted, you will be prompted to paste it.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save the downloaded video (default: '{DEFAULT_OUTPUT_DIR}').",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    url = args.url.strip() if args.url else None
    if not url or not is_valid_youtube_url(url):
        if url:
            print("That doesn't look like a valid YouTube URL.\n")
        url = prompt_for_url()

    print("\nFetching video info...")
    filepath = download_video(url, args.output)

    if filepath:
        print(f"\nDone! Video saved to: {filepath}")
        return 0

    print("\nSomething went wrong and the video could not be downloaded.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
