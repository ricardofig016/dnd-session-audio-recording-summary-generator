# AI Copilot Instructions for D&D Session Summary Generator

## Project Overview

This is a D&D session audio recording pipeline that automates transcription and summarization of tabletop gaming sessions. The system converts raw audio files into comprehensive markdown summaries using either local Whisper or OpenAI API for transcription, then DeepSeek API for LLM-powered summarization and formatting.

## Architecture & Data Flow

### Two Transcription Modes

**`main.py`** - Local Whisper transcription (requires GPU/CPU resources)

- Uses `whisper.load_model()` with local model (`"turbo"` or `"small"`)
- Fixed session number: hardcoded `SESSION_NUMBER = "14"`
- Requires: `whisper` package, local compute power
- Best for: batch processing without API costs

**`main_openai.py`** - OpenAI API transcription (cloud-based, recommended for production)

- Accepts audio file path as **command-line argument**: `python main_openai.py /path/to/audio.m4a`
- Extracts session folder name from filename (no extension): `test.m4a` → `sessions/test/`
- Flexible naming: accepts any audio file format (m4a, mp3, wav, etc.)
- Models available: `"whisper-1"` (default), `"gpt-4o-transcribe"` (higher quality), `"gpt-4o-mini-transcribe"`
- Requires: `OPENAI_API_KEY` in `.env`

### Pipeline Stages (Both Versions)

1. **Audio Transcription** → Raw text transcript (cached in `sessions/{name}/transcript.txt`)
2. **Summary Generation** → DeepSeek creates chronological summary with full session context
3. **Markdown Formatting** → DeepSeek applies markdown with Obsidian wikilinks (`[[Name]]`)

**Caching**: If transcript exists, transcription is skipped (promotes iterating on summarization).

### Data Organization

- **Sessions Directory**: `sessions/{session_name}/` contains:
  - `transcript.txt` → Raw transcription output
  - `summary.txt` → Unformatted comprehensive summary
  - `summary.md` → Formatted summary with wikilinks
- **Combined Sessions**: `combined_sessions.md` → Aggregated markdown from all previous sessions (used as LLM context, git-ignored)
- **Prompts Directory**: `prompts/` → Templates controlling LLM style:
  - `transcription.txt` → Context for transcription (game info, character names, language notes)
  - `summary.txt` → Rules for comprehensive event recording
  - `markdown.txt` → Rules for wikilink formatting and structure

### Supporting Scripts

- `campaign_summary.py`: Generates high-level campaign overview
- `custom_prompt.py`: Arbitrary queries on session transcripts
- `join_text.py`: Regenerates `combined_sessions.md` from all session markdown files
- `join_audios.py`, `split_audio.py`: Audio utilities

## Key Implementation Patterns

### Session Context Pattern (Critical for Consistency)

All LLM requests include **full context from all previous sessions** to maintain narrative continuity:

```python
content = f"{PROMPT}\n\nFor context, here are notes from all previous sessions in chronological order:\n{ALL_SESSION_NOTES}\n\nHere is the session transcript to summarize:\n{text}"
```

This is essential: the LLM needs character arcs, faction relationships, and story progression from prior sessions.

### Configuration & API Setup

**Environment Variables** (`.env`):

- `OPENAI_API_KEY` - Required for `main_openai.py`
- `DEEPSEEK_API_KEY` - Required for summarization (both scripts)

**API Clients**:

```python
# OpenAI (transcription only)
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# DeepSeek (summarization) - uses OpenAI SDK with custom base_url
DEEPSEEK_CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
response = DEEPSEEK_CLIENT.chat.completions.create(model="deepseek-reasoner", ...)
```

### OpenAI Transcription Specifics (`main_openai.py`)

```python
response = OPENAI_CLIENT.audio.transcriptions.create(
    model="whisper-1",          # or "gpt-4o-transcribe" for higher quality
    file=audio_file,            # Binary file object (not path)
    prompt=TRANSCRIPTION_PROMPT,  # Context about characters/terminology
    language="pt",              # Portuguese (primary language code)
    response_format="text",     # Plain text output
    temperature=0,              # Deterministic transcription
)
transcript_text = response  # Direct string, not response.text
```

### File Path Conventions

- Use **forward slashes** (`/`) for cross-platform compatibility
- Session folders: `os.path.join(CURRENT_DIRECTORY, f"sessions/{folder_name}")`
- Prompts: `os.path.join(CURRENT_DIRECTORY, "prompts/{filename}.txt")`
- SESSION_NOTES_DIRECTORY: External path (locally configured) for campaign context

### Prompt Template Patterns

**Summary Prompt Requirements**:

- Chronological recording of all events (major and minor)
- Per-NPC tracking: name, description, actions
- Obsidian wikilinks for locations, NPCs, factions, items
- Distinction: actual actions ≠ player speculation ≠ OOC banter
- Structured output with section tags (`### Scene:`, `### Combat:`, `### Puzzle:`)
- Present tense for event descriptions
- Mark unintelligible audio; only infer when reasonable

**Game Context**:

- Main characters with full names, nicknames, classes
- Companion NPCs and key factions
- Important locations and D&D 5e mechanics terminology
- Language note: Portuguese primary, transcribe as-is
- Expected: roleplay + mechanics discussion + code-switching

## Common Development Tasks

### Running Full Pipeline

**OpenAI Transcription (Recommended)**:

```powershell
# Ensure .env has OPENAI_API_KEY and DEEPSEEK_API_KEY
python main_openai.py "C:/path/to/my_session.m4a"
# Creates: sessions/my_session/{transcript.txt, summary.txt, summary.md}
```

**Local Whisper**:

```powershell
# Edit SESSION_NUMBER and AUDIO_FILE in main.py
python main.py
```

### Regenerate Campaign Context

```powershell
python join_text.py  # Rebuilds combined_sessions.md from all session markdown files
```

### Custom Analysis

```powershell
python custom_prompt.py  # Interactive: session number + your question
```

## Error Handling Conventions

- Missing API keys: Raise `ValueError` with key name
- File not found: Raise `FileNotFoundError` with expected path
- Empty files: Raise `ValueError` with context
- API timeouts: Report duration in seconds
- Requests to DeepSeek always use model `"deepseek-reasoner"` (enables extended reasoning)

## Performance & Optimization

- OpenAI transcription: ~30 seconds to 2 minutes depending on audio length
- DeepSeek summarization: Varies by token count; times reported in output
- Session context grows with each session (increases token count for future requests)
- Cached transcripts: Re-running script only does summarization (much faster iteration)
