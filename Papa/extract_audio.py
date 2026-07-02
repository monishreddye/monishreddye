"""Extract clean audio from Papa's interview videos."""

import subprocess
import sys
from pathlib import Path

from config import AUDIO_FOLDER, INTERVIEW_FOLDER, VOICE_SAMPLES_FOLDER


def run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed")


def extract_audio(video_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "1",
            str(output_path),
        ]
    )


def make_voice_sample(
    wav_path: Path, sample_path: Path, start_sec: int = 30, duration_sec: int = 90
) -> None:
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            str(wav_path),
            "-t",
            str(duration_sec),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "1",
            str(sample_path),
        ]
    )


def main() -> None:
    if not INTERVIEW_FOLDER.exists():
        print(f"Folder not found: {INTERVIEW_FOLDER}")
        print("Update INTERVIEW_FOLDER in config.py")
        sys.exit(1)

    videos = sorted(INTERVIEW_FOLDER.glob("*.mp4"))
    if not videos:
        print(f"No MP4 files found in {INTERVIEW_FOLDER}")
        sys.exit(1)

    print(f"Papa — found {len(videos)} interview video(s)\n")

    for index, video in enumerate(videos, start=1):
        wav_path = AUDIO_FOLDER / f"{video.stem}.wav"
        sample_path = VOICE_SAMPLES_FOLDER / f"{video.stem}_sample.wav"

        print(f"[{index}/{len(videos)}] Extracting: {video.name}")
        extract_audio(video, wav_path)
        make_voice_sample(wav_path, sample_path)
        print(f"  Audio: {wav_path}")
        print(f"  Voice sample: {sample_path}")

    print("\nDone.")
    print("Next: python transcribe_interviews.py")


if __name__ == "__main__":
    main()
