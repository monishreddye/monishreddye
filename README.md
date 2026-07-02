# monishreddye

## YouTube Video Downloader

A simple Python script that downloads a YouTube video to your local drive at the
**highest available quality**. It takes a YouTube link (typed or pasted),
inspects the available streams, and downloads the best video + best audio,
merging them into a single MP4 file.

### How it works

YouTube serves its highest resolutions (1080p, 1440p, 4K, ...) as **separate**
video and audio streams. This script uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
to grab the best of each and [`ffmpeg`](https://ffmpeg.org/) to merge them into
one file. If `ffmpeg` isn't installed, it falls back to the best single
pre-merged stream (which may be a lower resolution).

### Requirements

- Python 3.8+
- [`ffmpeg`](https://ffmpeg.org/download.html) installed and on your `PATH`
  (recommended, for full quality merging)

### Installation

```bash
pip install -r requirements.txt
```

Install `ffmpeg`:

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** download from https://ffmpeg.org/download.html and add it to your `PATH`

### Usage

Run the script and paste the link when prompted:

```bash
python youtube_downloader.py
```

Or pass the link directly as an argument:

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=XXXXXXXXXXX"
```

Choose a custom output folder:

```bash
python youtube_downloader.py "<link>" --output ~/Videos
```

By default, videos are saved to a `downloads/` folder in the current directory.
