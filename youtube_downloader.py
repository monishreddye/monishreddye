from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def prompt_for_url() -> str:
    """Prompt until the user enters a non-empty YouTube link."""
    while True:
        url = input("Enter or paste the YouTube video link: ").strip()
        if url:
            return url
        print("Please enter a valid YouTube link.")


def download_youtube_video(url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    options = {
        # Prefer highest video + highest audio, then fall back to best combined stream.
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
    }

    with YoutubeDL(options) as ydl:
        ydl.download([url])


def main() -> None:
    url = prompt_for_url()
    output_dir_text = input(
        "Enter download folder (press Enter for current folder): "
    ).strip()
    output_dir = Path(output_dir_text).expanduser() if output_dir_text else Path.cwd()

    try:
        download_youtube_video(url, output_dir)
    except DownloadError as error:
        print(f"Download failed: {error}")
        print(
            "Tip: install FFmpeg if the best video and audio streams need to be merged."
        )
    else:
        print(f"Download complete. Saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
