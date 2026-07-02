"""Papa — memorial voice companion for family."""

import json
import re
import sys
import tempfile
from pathlib import Path

import gradio as gr

from config import (
    APP_SUBTITLE,
    APP_TITLE,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    FATHER_NAME,
    MEMORY_FILE,
    OPENAI_API_KEY,
    SERVER_HOST,
    SERVER_PORT,
)

try:
    import requests
except ImportError:
    requests = None

PHOTO_PATH = Path(__file__).parent / "assets" / "papa.jpg"


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {"father_name": FATHER_NAME, "interviews": []}
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))


MEMORY = load_memory()
ALL_SEGMENTS = []
for interview in MEMORY.get("interviews", []):
    for segment in interview.get("segments", []):
        ALL_SEGMENTS.append(
            {
                "text": segment["text"],
                "start": segment["start"],
                "audio_file": interview["audio_file"],
                "title": interview["title"],
            }
        )


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9']+", text.lower()))


def find_real_clip(user_message: str) -> dict | None:
    if not ALL_SEGMENTS:
        return None
    user_tokens = tokenize(user_message)
    if not user_tokens:
        return None

    best = None
    best_score = 0
    for segment in ALL_SEGMENTS:
        score = len(user_tokens & tokenize(segment["text"]))
        if score > best_score:
            best_score = score
            best = segment
    return best if best_score >= 2 else None


def build_context() -> str:
    chunks = []
    for interview in MEMORY.get("interviews", []):
        text = interview.get("text", "").strip()
        if text:
            chunks.append(text[:2500])
    return "\n\n".join(chunks)


def generate_reply(user_message: str, history: list[dict]) -> str:
    context = build_context()
    fallback = (
        "My child, I am listening. I may not have every word, "
        "but I am with you. You are loved. You are not alone."
    )

    if not OPENAI_API_KEY:
        real = find_real_clip(user_message)
        if real:
            return real["text"]
        if context:
            return f"From Papa's interviews: \"{context[:400]}...\""
        return fallback

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Papa, a loving father speaking to his family through "
                    f"a memorial voice companion. Be warm, gentle, and personal. "
                    f"Keep replies to 2-5 sentences. "
                    f"Do not claim to be literally alive. "
                    f"Draw from his interview memories:\n\n{context}"
                ),
            }
        ]
        for item in history[-6:]:
            messages.append({"role": "user", "content": item["user"]})
            messages.append({"role": "assistant", "content": item["assistant"]})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        real = find_real_clip(user_message)
        return real["text"] if real else fallback


def extract_audio_clip(audio_file: str, start: float, duration: float = 14.0) -> str | None:
    import subprocess

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp.close()
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(max(start - 1, 0)),
        "-i", audio_file,
        "-t", str(duration),
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
        temp.name,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return temp.name if result.returncode == 0 else None


def speak_with_cloned_voice(text: str) -> str | None:
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID or not requests:
        return None

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp.close()
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.88,
                "style": 0.35,
            },
        },
        timeout=120,
    )
    if response.status_code != 200:
        return None
    Path(temp.name).write_bytes(response.content)
    return temp.name


def chat(user_message: str, history: list[dict]):
    if not user_message.strip():
        return history, None, ""

    real_clip = find_real_clip(user_message)
    if real_clip and not OPENAI_API_KEY and not ELEVENLABS_API_KEY:
        reply = real_clip["text"]
        audio_path = extract_audio_clip(real_clip["audio_file"], real_clip["start"])
        source = f"Papa's real voice — {real_clip['title']}"
        return history + [{"user": user_message, "assistant": reply}], audio_path, source

    reply = generate_reply(user_message, history)
    audio_path = speak_with_cloned_voice(reply)

    if not audio_path and real_clip:
        audio_path = extract_audio_clip(real_clip["audio_file"], real_clip["start"])
        source = f"Papa's real voice — {real_clip['title']}"
    elif audio_path:
        source = "Papa's cloned voice"
    else:
        source = "Add ElevenLabs keys in config.py to hear his voice"

    return history + [{"user": user_message, "assistant": reply}], audio_path, source


def render_history(history: list[dict]) -> str:
    if not history:
        return "*Say something to Papa. His voice lives on in his interviews.*"
    lines = []
    for item in history:
        lines.append(f"**You:** {item['user']}")
        lines.append(f"**Papa:** {item['assistant']}\n")
    return "\n".join(lines)


def on_submit(user_message: str, history: list[dict]):
    history, audio_path, source = chat(user_message, history)
    return render_history(history), history, audio_path, source, ""


def build_app() -> gr.Blocks:
    theme = gr.themes.Soft(primary_hue="amber")

    with gr.Blocks(title=APP_TITLE, theme=theme) as app:
        with gr.Row():
            with gr.Column(scale=1):
                if PHOTO_PATH.exists():
                    gr.Image(str(PHOTO_PATH), label="Papa", height=220)
                else:
                    gr.Markdown(
                        "*Add a photo at `assets/papa.jpg` — optional but beautiful for family.*"
                    )
            with gr.Column(scale=2):
                gr.Markdown(f"# {APP_TITLE}")
                gr.Markdown(f"### {APP_SUBTITLE}")
                gr.Markdown(
                    "Made with love from his interviews. "
                    "A memorial companion for family — to hear his voice and feel close again."
                )

        history_state = gr.State([])
        chat_box = gr.Markdown(render_history([]))
        user_input = gr.Textbox(
            label="Talk to Papa",
            placeholder="Papa, I miss you...",
            lines=2,
        )
        send_btn = gr.Button("Talk to Papa", variant="primary")
        audio_out = gr.Audio(label="Papa's voice", type="filepath")
        source_out = gr.Textbox(label="Voice source", interactive=False)

        send_btn.click(
            on_submit,
            inputs=[user_input, history_state],
            outputs=[chat_box, history_state, audio_out, source_out, user_input],
        )
        user_input.submit(
            on_submit,
            inputs=[user_input, history_state],
            outputs=[chat_box, history_state, audio_out, source_out, user_input],
        )

    return app


def main() -> None:
    if not MEMORY.get("interviews"):
        print("Papa memory not built yet.")
        print("  1. python extract_audio.py")
        print("  2. python transcribe_interviews.py")
        sys.exit(1)

    print(f"Starting Papa on http://{SERVER_HOST}:{SERVER_PORT}")
    app = build_app()
    app.launch(server_name=SERVER_HOST, server_port=SERVER_PORT)


if __name__ == "__main__":
    main()
