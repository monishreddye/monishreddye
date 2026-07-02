from pathlib import Path

# === Paths (edit for your computer) ===
INTERVIEW_FOLDER = Path(r"D:\Papa\YouTube Interviews")

DATA_FOLDER = Path(__file__).parent / "data"
AUDIO_FOLDER = DATA_FOLDER / "audio"
TRANSCRIPTS_FOLDER = DATA_FOLDER / "transcripts"
MEMORY_FILE = DATA_FOLDER / "papa_memory.json"
VOICE_SAMPLES_FOLDER = DATA_FOLDER / "voice_samples"

# === API keys (copy this file to config.py and fill in) ===
ELEVENLABS_API_KEY = ""
ELEVENLABS_VOICE_ID = ""

# Optional: warmer, more personal replies in Papa's style
OPENAI_API_KEY = ""

# === App branding ===
APP_NAME = "Papa"
APP_TITLE = "Papa"
APP_SUBTITLE = "Talk to him. Hear his voice. Feel him close again."
FATHER_NAME = "Papa"

# Gradio server (use 0.0.0.0 to share on home Wi‑Fi)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7860
