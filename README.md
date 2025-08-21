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

1. Change the path to your audio file in `main.py`
2. Run the main script:

   ```powershell
   python main.py
   ```

3. The script will process the audio and generate summaries in both markdown and plain text formats in each session folder.

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
