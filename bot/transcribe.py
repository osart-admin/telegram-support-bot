import os
import subprocess
from faster_whisper import WhisperModel

# Используем модель small для баланса между скоростью и качеством
model = WhisperModel("small", compute_type="int8")

def convert_to_wav(input_path: str, output_path: str):
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr.decode()}")

def transcribe_audio(file_path: str) -> str:
    try:
        wav_path = file_path.replace(".ogg", ".wav")
        convert_to_wav(file_path, wav_path)

        segments, _ = model.transcribe(wav_path)
        full_text = " ".join(segment.text for segment in segments)
        os.remove(wav_path)
        return full_text.strip()
    except Exception as e:
        print(f"[TRANSCRIBE ERROR] {e}")
        return ""
