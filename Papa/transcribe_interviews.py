"""Transcribe Papa's interviews and build his memory."""

import json
import sys
from pathlib import Path

from config import AUDIO_FOLDER, FATHER_NAME, MEMORY_FILE, TRANSCRIPTS_FOLDER

try:
    import whisper
except ImportError:
    print("Install dependencies first: pip install -r requirements.txt")
    sys.exit(1)


def transcribe_file(model, wav_path: Path) -> dict:
    print(f"Transcribing: {wav_path.name}")
    result = model.transcribe(str(wav_path), fp16=False)
    text = result.get("text", "").strip()
    segments = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        for seg in result.get("segments", [])
        if seg.get("text", "").strip()
    ]
    return {"text": text, "segments": segments}


def main() -> None:
    AUDIO_FOLDER.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_FOLDER.mkdir(parents=True, exist_ok=True)

    wav_files = sorted(AUDIO_FOLDER.glob("*.wav"))
    if not wav_files:
        print(f"No audio files in {AUDIO_FOLDER}")
        print("Run first: python extract_audio.py")
        sys.exit(1)

    print("Loading Whisper model (first run may take a few minutes)...")
    model = whisper.load_model("base")

    memory = {"father_name": FATHER_NAME, "interviews": []}

    for wav_path in wav_files:
        transcript = transcribe_file(model, wav_path)

        txt_path = TRANSCRIPTS_FOLDER / f"{wav_path.stem}.txt"
        txt_path.write_text(transcript["text"], encoding="utf-8")

        json_path = TRANSCRIPTS_FOLDER / f"{wav_path.stem}.json"
        json_path.write_text(
            json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        memory["interviews"].append(
            {
                "title": wav_path.stem,
                "audio_file": str(wav_path),
                "transcript_file": str(txt_path),
                "text": transcript["text"],
                "segments": transcript["segments"],
            }
        )
        print(f"  Saved: {txt_path}")

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nPapa memory saved: {MEMORY_FILE}")
    print("Next: clone voice at https://elevenlabs.io → update config.py")
    print("Then: python app.py")


if __name__ == "__main__":
    main()
