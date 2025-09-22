# DnD Session Summary Pipeline

This python script provides a pipeline for processing and summarizing Dungeons & Dragons session audio recordings. It helps automate the creation of concise summaries and formatted markdown files from raw audio files.

## Features

- Converts raw session audio recordings into readable markdown summaries

## Project Structure

```plaintext
project-root/
├── README.md
├── main.py
├── prompts
│   ├── markdown.txt
│   ├── summary.txt
│   └── transcription.txt
└── sessions
    ├── session_1.1
    │   ├── summary.md
    │   ├── summary.txt
    │   └── transcript.txt
    ├── session_2
    │   ├── summary.md
    │   ├── summary.txt
    │   └── transcript.txt
    └── session_test
        ├── summary.md
        ├── summary.txt
        └── transcript.txt
```

## Usage

1. Create the file `.env` at the project root with `DEEPSEEK_API_KEY=[your deepseek api key]`
2. Change the `AUDIO_FILE` variable in `main.py` to the path to your audio file
3. Run the main script:

   ```powershell
   python main.py
   ```

4. The script will process the audio and generate summaries in both markdown and plain text formats in each session folder.

## Requirements

- Python 3.7+
- The following Python packages.
  - whisper
  - dotenv
  - openai

To install them, run `pip install whisper python-dotenv openai`

## Customization

- Edit the prompt templates in the `prompts/` folder to adjust the summarization style or formatting.

## License

MIT License

## Author

Ricardo Figueiredo
