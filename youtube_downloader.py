#!/usr/bin/env python3
"""Download a YouTube video at the highest available quality."""

import argparse
import shutil
import sys
from pathlib import Path

import yt_dlp


DEFAULT_DOWNLOAD_DIR = Path(__file__).parent / "downloads"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a YouTube video at the highest available quality."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_DOWNLOAD_DIR,
        help="Folder to save the downloaded video (default: ./downloads)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help=(
            "Use browser cookies if YouTube asks you to sign in. "
            "Examples: chrome, firefox, edge, safari"
        ),
    )
    return parser.parse_args()


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is required to merge high-quality video and audio.")
        print("Install it with: sudo apt install ffmpeg  (Linux)")
        print("                 brew install ffmpeg       (macOS)")
        sys.exit(1)


def get_url() -> str:
    url = input("Enter or paste the YouTube link: ").strip()
    if not url:
        print("Error: No URL provided.")
        sys.exit(1)
    return url


def build_ydl_opts(output_dir: Path, cookies_browser: str | None = None) -> dict:
    opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title)s [%(height)sp].%(ext)s"),
        "noplaylist": True,
        "progress_hooks": [_progress_hook],
    }
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)
    return opts


def list_available_formats(url: str, ydl_opts: dict) -> None:
    probe_opts = {**ydl_opts, "quiet": True, "no_warnings": True}
    probe_opts.pop("progress_hooks", None)

    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    print(f"\nTitle: {info.get('title', 'Unknown')}")
    print(f"Channel: {info.get('uploader', 'Unknown')}")
    print(f"Duration: {info.get('duration_string', 'Unknown')}")
    print("\nTop available video formats:")

    formats = info.get("formats") or []
    video_formats = [
        f for f in formats if f.get("vcodec") != "none" and f.get("height")
    ]
    video_formats.sort(
        key=lambda f: (f.get("height", 0), f.get("fps", 0)), reverse=True
    )

    seen = set()
    for fmt in video_formats[:8]:
        key = (fmt.get("height"), fmt.get("ext"), fmt.get("vcodec"))
        if key in seen:
            continue
        seen.add(key)
        print(
            f"  - {fmt.get('height')}p | {fmt.get('ext')} | "
            f"{fmt.get('vcodec', 'unknown')} | ~{fmt.get('format_note', 'N/A')}"
        )

    best_audio = max(
        (
            f
            for f in formats
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ),
        key=lambda f: f.get("abr") or 0,
        default=None,
    )
    if best_audio:
        print(
            f"\nBest audio: {best_audio.get('ext')} | "
            f"{best_audio.get('acodec')} | ~{best_audio.get('abr', 'N/A')} kbps"
        )


def download_highest_quality(url: str, ydl_opts: dict) -> Path:
    output_dir = Path(ydl_opts["outtmpl"]).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info.get("requested_downloads"):
            filepath = Path(info["requested_downloads"][0]["filepath"])
        else:
            filepath = Path(ydl.prepare_filename(info)).with_suffix(".mp4")

    return filepath


def _progress_hook(status: dict) -> None:
    if status.get("status") == "downloading":
        total = status.get("total_bytes") or status.get("total_bytes_estimate")
        downloaded = status.get("downloaded_bytes", 0)
        if total:
            percent = downloaded / total * 100
            speed = status.get("speed")
            speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
            print(
                f"\rDownloading: {percent:.1f}% | {speed_str}",
                end="",
                flush=True,
            )
    elif status.get("status") == "finished":
        print("\rDownload complete. Merging video and audio...", flush=True)


def main() -> None:
    args = parse_args()
    check_ffmpeg()
    url = get_url()
    ydl_opts = build_ydl_opts(args.output_dir, args.cookies_from_browser)

    print("\nChecking available qualities...")
    try:
        list_available_formats(url, ydl_opts)
    except yt_dlp.utils.DownloadError as exc:
        print(f"\nError: Could not access video.\n{exc}")
        if "bot" in str(exc).lower():
            print(
                "\nTip: Retry with browser cookies, for example:\n"
                "  python youtube_downloader.py --cookies-from-browser chrome"
            )
        sys.exit(1)

    print(f"\nDownloading highest quality to: {args.output_dir.resolve()}")
    try:
        filepath = download_highest_quality(url, ydl_opts)
    except yt_dlp.utils.DownloadError as exc:
        print(f"\nError during download: {exc}")
        sys.exit(1)

    print(f"\nSaved to: {filepath.resolve()}")


if __name__ == "__main__":
    main()
