# YouTube Video Downloader

A simple Python script to download YouTube videos to your local drive at the
highest available video and audio quality.

## Features

- Paste a YouTube link interactively, or pass it as a command-line argument.
- Automatically detects and downloads the **best available video quality**
  and **best available audio quality**, then merges them into a single
  `.mp4` file (YouTube often serves high-resolution video and audio as
  separate streams, so merging is required to get the best quality in one
  file).
- Choose a custom output folder.
- Live download progress in the terminal.

## Requirements

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/download.html) installed and available on your
  `PATH` (required to merge separate video/audio streams).
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: download from the ffmpeg website and add it to `PATH`.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Interactive mode

Run the script and paste the link when prompted:

```bash
python youtube_downloader.py
```

```
Paste the YouTube video link: https://www.youtube.com/watch?v=VIDEO_ID
```

### Command-line mode

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Custom output folder

By default, videos are saved to a `downloads/` folder created next to the
script. Use `-o`/`--output` to change that:

```bash
python youtube_downloader.py "https://youtu.be/VIDEO_ID" -o ~/Videos
```

## Notes

- Only single videos are downloaded (playlists are ignored even if the link
  contains a playlist ID).
- If YouTube changes its site in a way that breaks downloading, update the
  `yt-dlp` package: `pip install -U yt-dlp`.
- Downloading content you don't have the rights to may violate YouTube's
  Terms of Service and copyright law. Use this tool responsibly and only for
  content you're permitted to download.
