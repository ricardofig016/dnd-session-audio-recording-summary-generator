# AI Copilot Instructions for D&D Session Summary Generator

## Project Overview

This is a D&D session audio recording pipeline that automates transcription and summarization of tabletop gaming sessions. The system converts raw audio files into comprehensive markdown summaries using OpenAI Whisper API for transcription, then the OpenAI Responses API for LLM-powered summarization and formatting.

## Architecture & Data Flow

### Two Transcription Modes

**`main_openai.py`** - OpenAI API transcription (recommended, production-ready)

- **Usage**: `python main_openai.py /path/to/audio.{m4a|mp3|wav}`
- Accepts audio file path as **command-line argument**
- Extracts session folder name from filename (no extension): `session17.m4a` → `sessions/session17/`
- Flexible naming: accepts any audio file format
- **Critical feature**: Automatically handles large files by splitting into MP3 chunks (max 25MB each)
  - Always splits, even single chunk for consistency
    - Uses `CHUNK_BITRATE = "48k"` (configurable, minimum quality for voice)
  - Chunks stored in `sessions/{name}/chunks/`
  - Individual chunk transcripts saved to `transcript_segments.txt`
  - All transcripts combined into `transcript.txt`
- Requires: `OPENAI_API_KEY` in `.env`
- Transcription models: `"whisper-1"` (default), `"gpt-4o-transcribe"` (higher quality)

**`main.py`** - Local Whisper transcription

- Uses `whisper.load_model()` with local model
- Fixed session number: hardcoded `SESSION_NUMBER = "14"`
- No API costs but requires GPU/CPU resources
- Best for: batch processing without external API calls

### Pipeline Stages (All Versions)

```
Audio File (any format)
    ↓
[Split into MP3 chunks if needed]
    ↓
Transcribe each chunk via OpenAI/Local Whisper
    ↓
Combine transcripts → transcript.txt
    ↓
Summarize with OpenAI Responses API (includes ALL prior session context)
    ↓
Generate Markdown with wikilinks via OpenAI Responses API
    ↓
Output: summary.txt, summary.md
```

**Key caching pattern**: If `transcript.txt` exists, transcription is skipped. This enables fast iteration on summarization prompts.

### Data Organization

- **Sessions Directory**: `sessions/{session_name}/`
  - `transcript.txt` - Combined transcription from all chunks
  - `transcript_segments.txt` - Individual chunk transcriptions (if multi-chunk)
  - `chunks/` - Temporary MP3 chunks and compression test file
  - `summary.txt` - Unformatted comprehensive summary
  - `summary.md` - Formatted summary with wikilinks
- **Campaign Context**: `combined_sessions.md` → Aggregated markdown from all sessions (git-ignored, used as LLM context)
- **Prompts Directory**: `prompts/` → Templates controlling LLM style
  - `transcription.txt` - Context for transcription (game info, character names)
  - `summary.txt` - Rules for comprehensive event recording (chronological, structured)
  - `markdown.txt` - Rules for wikilink formatting and structure

### Supporting Scripts

- **`custom_prompt.py`**: Arbitrary queries on specific session transcripts (interactive)
- **`campaign_summary.py`**: Generates high-level campaign overview
- **`join_text.py`**: Rebuilds `combined_sessions.md` from session markdown files
- **`join_audios.py`**, **`split_audio.py`**: Audio utilities

## Key Implementation Patterns

### Audio File Splitting (Critical for Large Files)

```python
# ALL audio files go through split_audio_into_chunks():
chunk_files = split_audio_into_chunks(audio_file)  # Returns list of MP3 files

# Algorithm:
# 1. Load audio, create test chunk (60 seconds)
# 2. Export test as MP3 with CHUNK_BITRATE → measure actual compressed size
# 3. Estimate full audio size: (test_size / 60000ms) * audio_duration
# 4. Calculate chunks needed: ceil(estimated_size / 25MB) * 1.2 (safety margin)
# 5. Split and export all chunks as MP3 with CHUNK_BITRATE
```

**Key variables**:

- `OPENAI_MAX_FILE_SIZE = 25 * 1024 * 1024` (API limit)
- `CHUNK_BITRATE = "64k"` (adjust here for quality/size tradeoff)

### Session Context Pattern (Critical for Narrative Continuity)

ALL LLM requests include **full context from all previous sessions** to maintain story arcs:

```python
# Pattern used in summarize_text(), generate_markdown_summary():
content = f"{PROMPT}\n\nFor context, here are notes from all previous sessions:\n{ALL_SESSION_NOTES}\n\nHere is the session transcript:\n{text}"

response = OPENAI_CLIENT.responses.create(
    model="gpt-5-mini",
    input=content,
)
```

This is essential: the LLM needs character arcs, relationships, and story progression from prior sessions for consistency.

### File Path Conventions

- Use **forward slashes** (`/`) for cross-platform compatibility
- Session folders: `os.path.join(CURRENT_DIRECTORY, f"sessions/{folder_name}")`
- Prompts: `os.path.join(CURRENT_DIRECTORY, "prompts/{filename}.txt")`
- SESSION_NOTES_DIRECTORY: External path (locally configured) for campaign context

### Configuration & API Setup

**Environment Variables** (`.env`):

```
OPENAI_API_KEY=sk-...
```

**API Clients**:

```python
# OpenAI (transcription)
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# OpenAI (summarization)
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
```

### Prompt Template Structure

All prompts are highly structured with specific sections:

**Summary Prompt** (`prompts/summary.txt`):

- Record ALL events (major and minor), not just highlights
- Per-NPC tracking: name, description, actions
- Distinguish: actual actions ≠ player speculation ≠ OOC banter
- Present tense for events, chronological structure
- Structured output with section tags: `### Scene:`, `### Combat:`, `### Puzzle:`, etc.
- Tables for NPCs, locations, ongoing threads
- Mark unintelligible audio explicitly; only infer when reasonable

**Markdown Prompt** (`prompts/markdown.txt`):

- Applies Obsidian wikilinks: `[[Character Name]]`, `[[Location]]`, `[[Faction]]`
- Maintains section structure and chronological order
- Formats for readability
- Preserves all content from summary

### OpenAI Transcription Details

```python
response = OPENAI_CLIENT.audio.transcriptions.create(
    model="whisper-1",                # Change to "gpt-4o-transcribe" for higher quality
    file=audio_file,                  # Open file object in binary mode
    prompt=TRANSCRIPTION_PROMPT,      # Context about characters/terminology
    language="pt",                    # Portuguese (configure per campaign)
    response_format="text",           # Plain text output
    temperature=0,                    # Deterministic transcription
)
transcript_text = response  # Direct string, not response.text
```

## Common Development Tasks

### Running Full Pipeline (Recommended)

```powershell
# Ensure .env has OPENAI_API_KEY
python main_openai.py "C:/path/to/my_session.m4a"
# Outputs to: sessions/my_session/{transcript.txt, summary.txt, summary.md}
```

### Iterate on Summarization (Without Re-transcribing)

```powershell
# 1. Edit prompts/summary.txt or prompts/markdown.txt
# 2. Delete sessions/{name}/summary.txt and summary.md (keep transcript.txt)
# 3. Re-run script - only summarization stages execute
python main_openai.py "C:/path/to/my_session.m4a"
```

### Regenerate Campaign Context

```powershell
python join_text.py  # Rebuilds combined_sessions.md from SESSION_NOTES_DIRECTORY
```

### Query Specific Session

```powershell
python custom_prompt.py  # Interactive: session number + your question
```

## Error Handling Conventions

- Missing API keys: Raise `ValueError` with key name
- File not found: Raise `FileNotFoundError` with expected path
- Empty files: Raise `ValueError` with context
- Transcription failures: Report duration and file size
- OpenAI Responses API timeouts: Retry or increase timeout
- Audio splitting failures: Check ffmpeg availability (pydub dependency)

## Performance & Optimization

- **OpenAI transcription**: 30 seconds to 2 minutes depending on audio length and chunk count
- **OpenAI summarization**: 2-5 minutes depending on transcript size
- **Session context growth**: Combined session context increases with each new session (token count grows)
- **Iteration workflow**: Delete summary files only (keep transcripts) for fast re-summarization
- **Audio compression**: 64k bitrate MP3 reduces file size ~5x vs WAV while maintaining voice clarity

## Common Pitfalls for AI Agents

1. **Don't skip audio splitting**: Even small files go through splitting for consistency
2. **Always include session context**: LLM requests without ALL prior sessions lose narrative continuity
3. **Use "gpt-5-mini" model**: Other models may change output quality and formatting
4. **Respect prompt structure**: Changing prompts requires understanding the specific formatting rules (tags, sections, tables)
5. **File path consistency**: Always use forward slashes; SESSION_NOTES_DIRECTORY is user-specific external path
