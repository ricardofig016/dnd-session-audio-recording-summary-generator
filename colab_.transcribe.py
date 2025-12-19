# !pip install openai-whisper
# !apt-get update -y
# !apt-get install -y ffmpeg
# !ffmpeg -version

import os
import time
import whisper

CURRENT_DIRECTORY = "./"
AUDIO_FILE = "./session12.m4a"  # CHANGE THIS
WHISPER_MODEL = "turbo"  # turbo for best results, small for faster results
TRANSCRIPT_FILE_NAME = "transcript.txt"


# Transcribe audio using Whisper
def transcribe_audio():
    print("Transcribing audio...")
    model = whisper.load_model(WHISPER_MODEL)

    start_time = time.time()
    result = model.transcribe(
        audio=AUDIO_FILE,
        verbose=True,
        initial_prompt="",
    )
    end_time = time.time()
    print(f"Transcription completed in { end_time - start_time:.2f} seconds.")

    transcript_path = os.path.join(CURRENT_DIRECTORY, TRANSCRIPT_FILE_NAME)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(result["text"])

    return result["text"]


# Main pipeline
def main():
    transcript = None
    transcript_path = os.path.join(CURRENT_DIRECTORY, TRANSCRIPT_FILE_NAME)
    transcript = transcribe_audio()


if __name__ == "__main__":
    main()
