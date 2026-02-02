# D&D Session Summary Generator from Audio Recordings

Automatically transcribes and summarizes D&D session audio recordings using OpenAI's Whisper API and the OpenAI Responses API for intelligent summarization with Obsidian wikilinks.

- [D\&D Session Summary Generator from Audio Recordings](#dd-session-summary-generator-from-audio-recordings)
  - [Quick Setup](#quick-setup)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [Workflow](#workflow)
  - [Utilities](#utilities)
  - [Advanced](#advanced)
  - [Requirements](#requirements)
  - [Troubleshooting](#troubleshooting)
  - [License](#license)
  - [Author](#author)

## Quick Setup

**1. Install dependencies:**

```powershell
pip install python-dotenv openai pydub
```

\*Note: `pydub` requires ffmpeg. Install via: `choco install ffmpeg` (Windows)

**2. Create `.env` file:**

```
OPENAI_API_KEY=your-key-here
```

**3. Run:**

```powershell
python main_openai.py "C:\path\to\audio.m4a"
```

Output: `sessions/audio_name/{transcript.txt, summary.txt, summary.md}`

## Features

- **Automatic Transcription** - OpenAI Whisper (cached)
- **Large File Handling** - Auto-splits files into MP3 chunks for API compliance
- **AI Summarization** - OpenAI Responses API with campaign context
- **Wikilinks** - Obsidian-style markdown
- **Session Context** - Maintains narrative continuity across all prior sessions
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
│       ├── transcript.txt           # Final combined transcript
│       ├── transcript_segments.txt  # Individual chunk transcripts (if multi-chunk)
│       ├── summary.txt
│       ├── summary.md
│       └── chunks/                  # Temporary MP3 chunks
├── combined_sessions.md     # All sessions aggregated (git-ignored)
├── custom_prompt.py         # Query specific sessions interactively
├── campaign_summary.py      # Generate campaign overview
├── join_text.py             # Rebuild combined_sessions.md
└── split_audio.py           # Standalone audio splitting utility
```

## Configuration

**Audio Chunking** (edit `main_openai.py` globals):

- `CHUNK_BITRATE = "48k"` - MP3 bitrate for audio chunks (minimum quality for voice transcription, reduce for faster processing)
- `OPENAI_MAX_FILE_SIZE = 25 * 1024 * 1024` - OpenAI API size limit (do not modify)

**Transcription** (edit `main_openai.py` globals):

- `OPENAI_TRANSCRIPTION_MODEL = "whisper-1"` - Change to `"gpt-4o-transcribe"` for higher quality
- `SESSION_NOTES_DIRECTORY = "..."` - Path to external session notes (used for campaign context)

**Summarization model** (edit `main_openai.py` globals):

- `SUMMARY_MODEL = "gpt-5-mini"` - Model used for summary and Markdown formatting

**Summarization** (edit `prompts/` files):

- `prompts/summary.txt` - Rules for comprehensive event recording (chronological, structured)
- `prompts/markdown.txt` - Rules for Obsidian wikilink formatting
- `prompts/transcription.txt` - Context about character names, terminology, language

## Workflow

1. **Audio Chunking** - File is automatically split into MP3 chunks if >25MB
   - Test chunk compressed to estimate full size
   - Chunks stored in `sessions/{name}/chunks/`
   - Always splits (even single chunk) for consistency
2. **Transcription** (cached) - OpenAI Whisper transcribes each chunk
   - Individual transcripts saved to `transcript_segments.txt`
   - Combined into `transcript.txt`
3. **Summarization** (with all prior session context, OpenAI Responses API) → `summary.txt`
4. **Markdown Formatting** (with Obsidian wikilinks, OpenAI Responses API) → `summary.md`

Each summary includes all previous sessions for narrative continuity.

## Utilities

- **`main.py`** - Local Whisper transcription (no API)
- **`custom_prompt.py`** - Query specific sessions
- **`campaign_summary.py`** - Campaign overview
- **`join_text.py`** - Rebuild `combined_sessions.md`
- **`join_audios.py`** & **`split_audio.py`** - Audio tools

## Advanced

**Iterate without re-transcribing:**

1. Edit `prompts/summary.txt` or `prompts/markdown.txt`
2. Delete `sessions/{name}/summary.txt` and `summary.md` (keep `transcript.txt`)
3. Re-run - only summarization and formatting stages execute

**Regenerate campaign context:**

```powershell
python join_text.py  # Rebuilds combined_sessions.md from SESSION_NOTES_DIRECTORY
```

**Query specific session interactively:**

```powershell
python custom_prompt.py  # Enter session number + custom question
```

## Requirements

- Python 3.8+
- Internet connection
- ffmpeg (for audio processing)
- OpenAI account with API credits (transcription and summarization)

## Troubleshooting

**Audio file exceeds size limit:**

- Automatic chunking handles this; ensure ffmpeg is installed
- Reduce `CHUNK_BITRATE` from `"64k"` to `"32k"` if chunks still exceed 25MB

**Transcription is slow:**

- Reduce `CHUNK_BITRATE` for faster compression (quality trade-off)
- Use `"gpt-4o-mini-transcribe"` model for faster processing

**Missing session context in summaries:**

- Verify `SESSION_NOTES_DIRECTORY` is correctly set
- Ensure session markdown files follow naming: `session X.md`
- Run `python join_text.py` to regenerate `combined_sessions.md`

## License

MIT

## Author

Ricardo Figueiredo
