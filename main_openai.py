import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI


def get_session_number(file):
    file_name = os.path.splitext(file)[0]
    session_number = float(file_name.split(" ")[1].strip())
    if session_number.is_integer():
        session_number = int(session_number)
    return session_number


def get_markdown_file_paths(notes_directory):
    files = {}
    for file in os.listdir(notes_directory):
        if file.lower().startswith("session") and file.endswith(".md"):
            session_number = get_session_number(file)
            files[session_number] = file
    file_paths = [os.path.join(notes_directory, files[key]) for key in sorted(files.keys())]
    return file_paths


def get_text_from_file(file):
    title = os.path.splitext(os.path.basename(file))[0]
    content = f"# {title}\n\n"
    with open(file, "r", encoding="utf-8") as f:
        content += f.read()
    return content


# Configuration
load_dotenv()

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

SESSION_NOTES_DIRECTORY = "C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/Finvora/Sessions"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

OPENAI_TRANSCRIPTION_MODEL = "whisper-1"  # or use "gpt-4o-transcribe" for better quality
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# DeepSeek configuration for summarization and markdown formatting
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is not set")

BASE_DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_DEEPSEEK_API_URL)

with open(os.path.join(CURRENT_DIRECTORY, "prompts/transcription.txt"), "r", encoding="utf-8") as file:
    TRANSCRIPTION_PROMPT = file.read()
with open(os.path.join(CURRENT_DIRECTORY, "prompts/summary.txt"), "r", encoding="utf-8") as file:
    SUMMARY_PROMPT = file.read()
with open(os.path.join(CURRENT_DIRECTORY, "prompts/markdown.txt"), "r", encoding="utf-8") as file:
    MARKDOWN_PROMPT = file.read()

TRANSCRIPT_FILE_NAME = "transcript.txt"
SUMMARY_FILE_NAME = "summary.txt"
MARKDOWN_SUMMARY_FILE_NAME = "summary.md"

SESSION_DIRECTORY = ""  # Will be set based on audio file path
ALL_SESSION_NOTES = ""  # Will be loaded from session notes directory


# Transcribe audio using OpenAI API
def transcribe_audio(audio_file):
    print("Transcribing audio using OpenAI API...")

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Open audio file in binary mode
    with open(audio_file, "rb") as file:
        start_time = time.time()
        response = OPENAI_CLIENT.audio.transcriptions.create(
            model=OPENAI_TRANSCRIPTION_MODEL,
            file=file,
            prompt=TRANSCRIPTION_PROMPT,
            language="pt",  # Portuguese as primary language
            response_format="text",
            temperature=0,  # Deterministic output
        )
        end_time = time.time()

    transcript_text = response
    print(f"Transcription completed in {end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    transcript_path = os.path.join(SESSION_DIRECTORY, TRANSCRIPT_FILE_NAME)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(transcript_text)

    return transcript_text


# Summarize the transcript
def summarize_text(text_transcript):
    print("Summarizing text...")

    start_time = time.time()
    response = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": f"{SUMMARY_PROMPT}\n\nFor context, here are notes from all previous sessions in chronological order:\n{ALL_SESSION_NOTES}\n\nHere is the session transcript to summarize:\n{text_transcript}",
            },
        ],
        stream=False,
    )
    summarized_text = response.choices[0].message.content
    end_time = time.time()
    print(f"Summarization completed in {end_time - start_time:.2f} seconds.")

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
                "content": f"{MARKDOWN_PROMPT}\n\nFor context, here are notes from all previous sessions in chronological order:\n{ALL_SESSION_NOTES}\n\nHere is the session summary to format in Markdown:\n{text}",
            },
        ],
        stream=False,
    )
    markdown_text = response.choices[0].message.content
    end_time = time.time()
    print(f"Markdown generation completed in {end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    markdown_path = os.path.join(SESSION_DIRECTORY, MARKDOWN_SUMMARY_FILE_NAME)
    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(markdown_text)
    return markdown_text


# Main pipeline
def main():
    # Check if audio file path is provided
    if len(sys.argv) < 2:
        print("Usage: python main_openai.py <audio_file_path>")
        print("Example: python main_openai.py 'C:/path/to/my_audio.m4a'")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Get filename without extension for folder name
    file_name = os.path.splitext(os.path.basename(audio_file))[0]

    # Setup session directory and configuration
    global SESSION_DIRECTORY, ALL_SESSION_NOTES
    SESSION_DIRECTORY = os.path.join(CURRENT_DIRECTORY, f"sessions/{file_name}")

    # Load session notes and create combined_sessions.md
    SESSION_NOTES_FILES = get_markdown_file_paths(SESSION_NOTES_DIRECTORY)
    ALL_SESSION_NOTES = ""
    for notes_file in SESSION_NOTES_FILES:
        ALL_SESSION_NOTES += get_text_from_file(notes_file) + f"\n\n{'='*40}\n\n"

    # Save to file
    with open("combined_sessions.md", "w", encoding="utf-8") as file:
        file.write(ALL_SESSION_NOTES.strip())

    # Process audio file
    transcript = None
    transcript_path = os.path.join(SESSION_DIRECTORY, TRANSCRIPT_FILE_NAME)
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as file:
            transcript = file.read()
    if not transcript:
        transcript = transcribe_audio(audio_file)

    summary = summarize_text(transcript)
    markdown_summary = generate_markdown_summary(summary)

    markdown_summary_path = os.path.join(SESSION_DIRECTORY, MARKDOWN_SUMMARY_FILE_NAME)
    print(f"Summary saved to {markdown_summary_path}")


if __name__ == "__main__":
    main()
