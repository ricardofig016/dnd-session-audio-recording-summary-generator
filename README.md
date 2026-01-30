# D&D Session Summary Generator from Audio Recordings

Automatically transcribes and summarizes D&D session audio recordings using OpenAI's Whisper API and DeepSeek for intelligent summarization with Obsidian wikilinks.

- [D\&D Session Summary Generator from Audio Recordings](#dd-session-summary-generator-from-audio-recordings)
  - [Quick Setup](#quick-setup)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [Workflow](#workflow)
  - [Utilities](#utilities)
  - [Advanced](#advanced)
  - [Requirements](#requirements)
  - [License](#license)
  - [Author](#author)

## Quick Setup

**1. Install dependencies:**

```powershell
pip install python-dotenv openai
```

**2. Create `.env` file:**

```
OPENAI_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
```

**3. Run:**

```powershell
python main_openai.py "C:\path\to\audio.m4a"
```

Output: `sessions/audio_name/{transcript.txt, summary.txt, summary.md}`

## Features

- **Automatic Transcription** - OpenAI Whisper (cached)
- **AI Summarization** - DeepSeek with campaign context
- **Wikilinks** - Obsidian-style markdown
- **Session Context** - Maintains narrative continuity
- **Audio Formats** - m4a, mp3, wav, etc.

---

## Project Structure

```
├── main_openai.py           # Primary workflow
├── main.py                  # Local Whisper alternative
├── prompts/
│   ├── transcription.txt    # Whisper context
│   ├── summary.txt          # Summarization rules
│   └── markdown.txt         # Wikilink formatting
├── sessions/                # Session outputs
│   └── session_name/
│       ├── transcript.txt
│       ├── summary.txt
│       └── summary.md
└── combined_sessions.md     # All sessions aggregated
```

## Configuration

**Optional:** Edit `main_openai.py` to:

- Change transcription model: `OPENAI_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"` (higher quality)
- Adjust session notes directory: `SESSION_NOTES_DIRECTORY = "..."`

Customize prompts in `prompts/` folder to adjust style, detail level, or wikilink aggressiveness.

## Workflow

1. **Transcription** (cached) → `transcript.txt`
2. **Summarization** (with prior sessions) → `summary.txt`
3. **Markdown Formatting** (with wikilinks) → `summary.md`

Each summary includes all previous sessions for narrative continuity.

## Utilities

- **`main.py`** - Local Whisper transcription (no API)
- **`custom_prompt.py`** - Query specific sessions
- **`campaign_summary.py`** - Campaign overview
- **`join_text.py`** - Rebuild `combined_sessions.md`
- **`join_audios.py`** & **`split_audio.py`** - Audio tools

## Advanced

**Iterate without re-transcribing:**

1. Edit `prompts/summary.txt`
2. Delete `summary.txt` and `summary.md`
3. Re-run (only summarization stages)

## Requirements

- Python 3.8+
- Internet connection
- OpenAI account with credits
- DeepSeek account with credits

## License

MIT

## Author

Ricardo Figueiredo
