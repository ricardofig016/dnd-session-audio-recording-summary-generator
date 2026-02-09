import os
import shutil
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment


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

OPENAI_TRANSCRIPTION_MODEL = "whisper-1"
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

SUMMARY_MODEL = "gpt-5-mini"

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

# OpenAI API limits
OPENAI_MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB in bytes
CHUNK_BITRATE = "48k"  # MP3 bitrate for audio chunks


# Split audio file into chunks if it exceeds the size limit
def split_audio_into_chunks(audio_file):
    """Split audio files into chunks under 25MB."""
    file_size = os.path.getsize(audio_file)

    print(f"Audio file size ({file_size / (1024*1024):.2f} MB). Processing into chunks...")

    # Load audio file
    audio = AudioSegment.from_file(audio_file)
    audio_duration = len(audio)  # Duration in milliseconds

    # Create chunks directory
    chunks_dir = os.path.join(SESSION_DIRECTORY, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    # Export a test chunk to estimate final compressed size
    print("Calculating optimal chunk count based on compressed size...")
    test_chunk = audio[:60000]  # First 60 seconds
    test_file = os.path.join(chunks_dir, "test_chunk.mp3")
    test_chunk.export(test_file, format="mp3", bitrate=CHUNK_BITRATE)
    test_size = os.path.getsize(test_file)
    os.remove(test_file)

    # Estimate full audio size after compression
    estimated_full_size = (test_size / 60000) * audio_duration

    # Calculate number of chunks needed (with safety margin)
    num_chunks = int((estimated_full_size / OPENAI_MAX_FILE_SIZE) * 1.2) + 1
    chunk_duration = audio_duration // num_chunks

    print(f"Splitting into {num_chunks} chunks...")

    # Split and save chunks
    chunk_files = []
    for i in range(num_chunks):
        start_time = i * chunk_duration
        end_time = (i + 1) * chunk_duration if i < num_chunks - 1 else audio_duration

        chunk = audio[start_time:end_time]
        chunk_file = os.path.join(chunks_dir, f"chunk_{i+1}.mp3")
        chunk.export(chunk_file, format="mp3", bitrate=CHUNK_BITRATE)
        chunk_files.append(chunk_file)

        chunk_size = os.path.getsize(chunk_file)
        print(f"  Chunk {i+1}/{num_chunks}: {chunk_size / (1024*1024):.2f} MB")

    return chunk_files


# Transcribe audio using OpenAI API
def transcribe_audio(audio_file):
    print("Transcribing audio using OpenAI API...")

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Split audio if needed
    chunk_files = split_audio_into_chunks(audio_file)

    # Transcribe each chunk
    all_transcripts = []
    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"Transcribing chunk {i}/{len(chunk_files)}...")

        with open(chunk_file, "rb") as file:
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
        all_transcripts.append(transcript_text)
        print(f"Chunk {i} transcription completed in {end_time - start_time:.2f} seconds.")

    # Combine all transcripts
    combined_transcript = "\n\n".join(all_transcripts)
    print(f"All transcriptions completed. Total chunks: {len(chunk_files)}")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)

    # Save individual chunk transcripts if multiple chunks
    if len(chunk_files) > 1:
        segments_path = os.path.join(SESSION_DIRECTORY, "transcript_segments.txt")
        with open(segments_path, "w", encoding="utf-8") as file:
            for i, transcript in enumerate(all_transcripts, 1):
                file.write(f"=== Chunk {i} ===\n\n")
                file.write(transcript)
                file.write("\n\n")
        print(f"Individual chunk transcripts saved to {segments_path}")

    # Save combined transcript
    transcript_path = os.path.join(SESSION_DIRECTORY, TRANSCRIPT_FILE_NAME)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(combined_transcript)

    # Clean up temporary chunks directory
    chunks_dir = os.path.join(SESSION_DIRECTORY, "chunks")
    if os.path.exists(chunks_dir):
        shutil.rmtree(chunks_dir)
        print(f"Cleaned up temporary chunks directory")

    return combined_transcript


# Summarize the transcript
def summarize_text(text_transcript, file_name):
    print("Summarizing text...")

    start_time = time.time()
    response = OPENAI_CLIENT.responses.create(
        model=SUMMARY_MODEL,
        input=(
            f"{SUMMARY_PROMPT}\n\nFor context, here are notes from the previous 10 sessions in chronological order:\n"
            f"{ALL_SESSION_NOTES}\n\nHere is the session transcript to summarize of session {file_name}:\n{text_transcript}"
        ),
    )
    summarized_text = "".join(item.text for output in response.output if output.type == "message" for item in output.content if item.type == "output_text")
    end_time = time.time()
    print(f"Summarization completed in {end_time - start_time:.2f} seconds.")

    os.makedirs(SESSION_DIRECTORY, exist_ok=True)
    summarized_path = os.path.join(SESSION_DIRECTORY, SUMMARY_FILE_NAME)
    with open(summarized_path, "w", encoding="utf-8") as file:
        file.write(summarized_text)
    return summarized_text


# Generate Markdown summary
def generate_markdown_summary(text, file_name):
    print("Generating Markdown text...")

    start_time = time.time()
    response = OPENAI_CLIENT.responses.create(
        model=SUMMARY_MODEL,
        input=(
            f"{MARKDOWN_PROMPT}\n\nFor context, here are notes from the previous 10 sessions in chronological order:\n"
            f"{ALL_SESSION_NOTES}\n\nHere is the session summary to format in Markdown of session {file_name}:\n{text}"
        ),
    )
    markdown_text = "".join(item.text for output in response.output if output.type == "message" for item in output.content if item.type == "output_text")
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

    # Load session notes and create combined_sessions.md (last 10 sessions only)
    SESSION_NOTES_FILES = get_markdown_file_paths(SESSION_NOTES_DIRECTORY)
    # Take only the last 10 sessions to reduce context consumption
    SESSION_NOTES_FILES = SESSION_NOTES_FILES[-10:]
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

    summary = summarize_text(transcript, file_name)
    markdown_summary = generate_markdown_summary(summary, file_name)

    markdown_summary_path = os.path.join(SESSION_DIRECTORY, MARKDOWN_SUMMARY_FILE_NAME)
    print(f"Summary saved to {markdown_summary_path}")


if __name__ == "__main__":
    main()
