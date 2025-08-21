import os
import time
import whisper
from dotenv import load_dotenv
from openai import OpenAI


# Configuration
load_dotenv()

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

SESSION_NUMBER = "2"
FILE_FORMAT = "m4a"
AUDIO_FILE = f"C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/assets/session {SESSION_NUMBER} audio.{FILE_FORMAT}"
WHISPER_MODEL = "turbo"  # turbo for best results, small for faster results

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set")

BASE_DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_DEEPSEEK_API_URL)

with open(
    os.path.join(CURRENT_DIRECTORY, "prompts/transcription.txt"), "r", encoding="utf-8"
) as file:
    TRANSCRIPTION_PROMPT = file.read()
with open(
    os.path.join(CURRENT_DIRECTORY, "prompts/summary.txt"), "r", encoding="utf-8"
) as file:
    SUMMARY_PROMPT = file.read()
with open(
    os.path.join(CURRENT_DIRECTORY, "prompts/markdown.txt"), "r", encoding="utf-8"
) as file:
    MARKDOWN_PROMPT = file.read()

SESSION_DIRECTORY = os.path.join(
    CURRENT_DIRECTORY, f"sessions/session_{SESSION_NUMBER}"
)

TRANSCRIPT_FILE_NAME = "transcript.txt"
SUMMARY_FILE_NAME = "summary.txt"
MARKDOWN_SUMMARY_FILE_NAME = "summary.md"


# Transcribe audio using Whisper
def transcribe_audio():
    print("Transcribing audio...")
    model = whisper.load_model(WHISPER_MODEL)

    start_time = time.time()
    result = model.transcribe(
        audio=AUDIO_FILE,
        verbose=True,
        initial_prompt=TRANSCRIPTION_PROMPT,
    )
    end_time = time.time()
    print(f"Transcription completed in { end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    transcript_path = os.path.join(SESSION_DIRECTORY, TRANSCRIPT_FILE_NAME)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(result["text"])

    return result["text"]


# Summarize the transcript
def summarize_text(text):
    print("Summarizing text...")

    start_time = time.time()
    response = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": f"{SUMMARY_PROMPT}\n\n{text}",
            },
        ],
        stream=False,
    )
    summarized_text = response.choices[0].message.content
    end_time = time.time()
    print(f"Summarization completed in { end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    summarized_path = os.path.join(SESSION_DIRECTORY, SUMMARY_FILE_NAME)
    with open(summarized_path, "w", encoding="utf-8") as file:
        file.write(summarized_text)
    return summarized_text


# Generate Markdown summary
def generate_markdown_summary(text):
    print("Generating Markdown text...")

    start_time = time.time()
    response = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": f"{MARKDOWN_PROMPT}\n\n{text}",
            },
        ],
        stream=False,
    )
    markdown_text = response.choices[0].message.content
    end_time = time.time()
    print(f"Markdown generation completed in { end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    markdown_path = os.path.join(SESSION_DIRECTORY, MARKDOWN_SUMMARY_FILE_NAME)
    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(markdown_text)
    return markdown_text


# Main pipeline
def main():
    transcript = None
    transcript_path = os.path.join(SESSION_DIRECTORY, TRANSCRIPT_FILE_NAME)
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as file:
            transcript = file.read()
    if not transcript:
        transcript = transcribe_audio()

    summary = summarize_text(transcript)
    markdown_summary = generate_markdown_summary(summary)

    markdown_summary_path = os.path.join(SESSION_DIRECTORY, MARKDOWN_SUMMARY_FILE_NAME)
    print(f"Summary for Session {SESSION_NUMBER} saved to {markdown_summary_path}")


if __name__ == "__main__":
    main()
