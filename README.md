# YouTube Video Downloader

A simple Python script that downloads a YouTube video to your local drive at
the **highest video quality available**, with audio included.

## How it works

1. You enter (or paste) a YouTube link when prompted.
2. The script inspects the video and picks the best video stream and the best
   audio stream available.
3. Both streams are downloaded and merged into a single MP4 file, saved to
   `~/Downloads/YouTube` (created automatically if it doesn't exist).

## Requirements

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your PATH
  (needed to merge the highest-quality video and audio streams; without it,
  the script falls back to the best pre-merged quality)

Install the Python dependency:

```bash
pip install -r requirements.txt
```

## Usage

Run interactively and paste the link when prompted:

```bash
python youtube_downloader.py
```

Or pass the link directly as an argument:

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The downloaded file will appear in `~/Downloads/YouTube`.
