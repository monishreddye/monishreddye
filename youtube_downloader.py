#!/usr/bin/env python3
"""
YouTube Video Downloader
Downloads YouTube videos at the highest available quality (video + audio merged).
"""

import os
import sys

try:
    import yt_dlp
except ImportError:
    print("Required package 'yt-dlp' is not installed.")
    print("Install it with:  pip install yt-dlp")
    sys.exit(1)


def get_download_directory() -> str:
    """Return the user's Downloads folder, falling back to the current directory."""
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    if os.path.isdir(downloads):
        return downloads
    return os.getcwd()


def show_available_formats(url: str) -> None:
    """Print all available formats for a given URL (for informational purposes)."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        print(f"\n{'─' * 60}")
        print(f"  Title  : {info.get('title', 'Unknown')}")
        print(f"  Channel: {info.get('uploader', 'Unknown')}")
        print(f"  Length : {info.get('duration_string', 'Unknown')}")
        print(f"{'─' * 60}")

        # Show only video+audio combined formats and best separate streams
        combined = [
            f for f in formats
            if f.get("vcodec") != "none" and f.get("acodec") != "none"
        ]
        print("\n  Combined (video + audio) formats:")
        print(f"  {'ID':<12} {'Ext':<6} {'Resolution':<14} {'FPS':<6} {'Size'}")
        print(f"  {'─'*12} {'─'*6} {'─'*14} {'─'*6} {'─'*12}")
        for f in combined[-10:]:  # show up to 10 best
            size = f.get("filesize") or f.get("filesize_approx")
            size_str = f"{size / 1_048_576:.1f} MB" if size else "N/A"
            print(
                f"  {f.get('format_id',''):<12} "
                f"{f.get('ext',''):<6} "
                f"{f.get('resolution',''):<14} "
                f"{str(f.get('fps','')):<6} "
                f"{size_str}"
            )
        print()


def progress_hook(d: dict) -> None:
    """Display a live download progress bar."""
    if d["status"] == "downloading":
        percent    = d.get("_percent_str", "N/A").strip()
        speed      = d.get("_speed_str", "N/A").strip()
        eta        = d.get("_eta_str", "N/A").strip()
        downloaded = d.get("_downloaded_bytes_str", "").strip()
        total      = d.get("_total_bytes_str", "") or d.get("_total_bytes_estimate_str", "")
        total      = total.strip()
        bar_info   = f"{downloaded} / {total}" if total else downloaded
        print(
            f"\r  [{percent}]  {bar_info}  Speed: {speed}  ETA: {eta}   ",
            end="",
            flush=True,
        )
    elif d["status"] == "finished":
        print(f"\r  Download complete — merging audio/video if needed …{' ' * 20}")
    elif d["status"] == "error":
        print(f"\n  [ERROR] {d.get('error', 'Unknown error')}")


def download_video(url: str, output_dir: str) -> None:
    """Download the YouTube video at the best quality and save it to output_dir."""

    # Format selector:
    #   bestvideo+bestaudio  → best separate streams merged via ffmpeg (highest quality)
    #   /best                → fallback to best single-file stream if merge is unavailable
    format_selector = "bestvideo+bestaudio/best"

    output_template = os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s")

    ydl_opts = {
        "format": format_selector,
        "outtmpl": output_template,
        "merge_output_format": "mp4",   # merge into MP4 container
        "progress_hooks": [progress_hook],
        "noplaylist": True,             # download only the single video, not a playlist
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }

    print(f"\n  Saving to: {output_dir}")
    print(f"  Format   : best video + best audio  →  MP4\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("\n  Done! Your video has been saved.\n")


def validate_url(url: str) -> bool:
    """Basic check that the string looks like a URL."""
    return url.startswith("http://") or url.startswith("https://")


def main() -> None:
    print("=" * 60)
    print("        YouTube Video Downloader — Highest Quality")
    print("=" * 60)

    # Accept URL from command-line argument or prompt the user
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
        print(f"\n  URL: {url}")
    else:
        print("\n  Paste the YouTube video URL and press Enter.")
        print("  (Type 'q' to quit)\n")
        url = input("  URL: ").strip()

    if url.lower() in ("q", "quit", "exit", ""):
        print("\n  Exiting. Goodbye!")
        sys.exit(0)

    if not validate_url(url):
        print("\n  [ERROR] That doesn't look like a valid URL.")
        print("  Make sure it starts with https:// or http://")
        sys.exit(1)

    # Fetch and display video metadata
    print("\n  Fetching video information …")
    try:
        show_available_formats(url)
    except yt_dlp.utils.DownloadError as exc:
        print(f"\n  [ERROR] Could not fetch video info:\n  {exc}")
        sys.exit(1)

    # Ask where to save (default: ~/Downloads or cwd)
    default_dir = get_download_directory()
    print(f"  Where should the file be saved?")
    print(f"  Press Enter to use the default: {default_dir}")
    user_dir = input("  Directory: ").strip()
    output_dir = user_dir if user_dir else default_dir

    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"  Created directory: {output_dir}")
        except OSError as exc:
            print(f"\n  [ERROR] Cannot create directory '{output_dir}': {exc}")
            sys.exit(1)

    # Download
    print("\n  Starting download …")
    try:
        download_video(url, output_dir)
    except yt_dlp.utils.DownloadError as exc:
        print(f"\n  [ERROR] Download failed:\n  {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n  Download cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
