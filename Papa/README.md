# Papa

A private memorial voice companion for family — built from Papa's interview recordings.

Talk to him. Hear his voice. Feel him close again.

## What Papa does

- Extracts audio from his interview videos
- Learns what he said (transcription + memory)
- Clones his voice (ElevenLabs) for new replies
- Lets family chat and hear him in a simple web app

## Setup (Windows)

### 1. Clone this private repo

```bash
git clone https://github.com/monishreddye/Papa.git
cd Papa
```

### 2. Install Python 3.10+ and ffmpeg

- Python: https://python.org
- ffmpeg: https://ffmpeg.org/download.html

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

```bash
copy config.example.py config.py
```

Edit `config.py`:

- `INTERVIEW_FOLDER` → `D:\Papa\YouTube Interviews`
- Add ElevenLabs API key + voice ID (after voice clone)
- Optional: OpenAI API key for warmer replies

### 5. Download interviews (if needed)

```bash
python youtube_downloader.py
```

### 6. Build Papa's voice memory

```bash
python extract_audio.py
python transcribe_interviews.py
```

### 7. Clone Papa's voice

1. Go to https://elevenlabs.io
2. Voice Lab → Instant Voice Clone
3. Upload samples from `data/voice_samples/`
4. Copy Voice ID + API key into `config.py`

### 8. Run Papa

```bash
python app.py
```

Open http://127.0.0.1:7860 in your browser.

### Optional: add his photo

Place a photo at `assets/papa.jpg` — it will show in the app for family.

### Share with family on home Wi‑Fi

In `config.py` set:

```python
SERVER_HOST = "0.0.0.0"
```

Family on the same Wi‑Fi can open `http://YOUR-PC-IP:7860`.

## Project structure

```
Papa/
  app.py                  # Main family app
  extract_audio.py        # Step 1: audio from videos
  transcribe_interviews.py # Step 2: build memory
  youtube_downloader.py   # Helper: download interviews
  config.example.py       # Settings template
  assets/papa.jpg         # Optional photo
  data/                   # Generated (not in git)
```

## Built with love

This app is a memorial companion — not a replacement. Papa lives on in his words, his voice, and your memories.
