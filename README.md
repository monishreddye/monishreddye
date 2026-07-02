# YouTube Video Downloader

This project includes a Python script that asks for a YouTube link, checks the
best quality available, and downloads the video to your local drive.

## Requirements

- Python 3.9 or newer
- FFmpeg installed on your computer
- Python dependencies from `requirements.txt`

FFmpeg is important because YouTube often provides the highest video quality and
best audio as separate streams. The script uses FFmpeg through `yt-dlp` to merge
them into one MP4 file.

## Setup

```bash
pip install -r requirements.txt
```

Install FFmpeg if it is not already available:

- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS with Homebrew: `brew install ffmpeg`
- Windows: download it from <https://ffmpeg.org/download.html> and add it to PATH

## Run

```bash
python youtube_downloader.py
```

Then paste the YouTube link when asked. You can also enter a download folder, or
press Enter to save the file in the current folder.
