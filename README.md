# D&D Session Audio Recording & Summary Generator

A Python pipeline that automatically transcribes and summarizes Dungeons & Dragons session audio recordings. This tool converts raw audio files into comprehensive markdown summaries using OpenAI's Whisper API for transcription and DeepSeek's API for intelligent summarization and formatting.

## Table of Contents

- [D\&D Session Audio Recording \& Summary Generator](#dd-session-audio-recording--summary-generator)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [One-Minute Setup](#one-minute-setup)
  - [Prerequisites \& Installation](#prerequisites--installation)
    - [System Requirements](#system-requirements)
    - [Step 1: Install Python Packages](#step-1-install-python-packages)
    - [Step 2: Get API Keys](#step-2-get-api-keys)
  - [Configuration](#configuration)
    - [Environment Variables (.env)](#environment-variables-env)
    - [Optional: Adjust Session Notes Directory](#optional-adjust-session-notes-directory)
    - [Optional: Change Transcription Model](#optional-change-transcription-model)
  - [Main Workflow: main_openai.py](#main-workflow-main_openaipy)
    - [Basic Usage](#basic-usage)
    - [Understanding the Pipeline](#understanding-the-pipeline)
      - [Stage 1: Transcription (Optional - Cached)](#stage-1-transcription-optional---cached)
      - [Stage 2: Summarization](#stage-2-summarization)
      - [Stage 3: Markdown Formatting \& Wikilinks](#stage-3-markdown-formatting--wikilinks)
    - [Output Files](#output-files)
  - [Project Structure](#project-structure)
  - [Prompt Customization](#prompt-customization)
    - [prompts/transcription.txt](#promptstranscriptiontxt)
    - [prompts/summary.txt](#promptssummarytxt)
    - [prompts/markdown.txt](#promptsmarkdowntxt)
  - [Advanced Usage](#advanced-usage)
    - [Iterate on Summaries Without Re-Transcribing](#iterate-on-summaries-without-re-transcribing)
    - [Use Higher-Quality Transcription](#use-higher-quality-transcription)
    - [Regenerate Campaign Context](#regenerate-campaign-context)
    - [Custom Queries on Transcripts](#custom-queries-on-transcripts)
    - [Generate Campaign Summary](#generate-campaign-summary)
    - [Merge Audio Files](#merge-audio-files)
    - [Split Long Audio](#split-long-audio)
  - [Other Utilities](#other-utilities)
    - [main.py - Local Whisper Transcription](#mainpy---local-whisper-transcription)
    - [custom_prompt.py - Arbitrary Session Queries](#custom_promptpy---arbitrary-session-queries)
    - [campaign_summary.py - High-Level Campaign Overview](#campaign_summarypy---high-level-campaign-overview)
    - [join_text.py - Rebuild Campaign Context](#join_textpy---rebuild-campaign-context)
    - [join_audios.py \& split_audio.py](#join_audiospy--split_audiopy)
  - [License](#license)
  - [Author](#author)

---

## Features

- **OpenAI Transcription**: Uses Whisper-1 API (or higher-quality options) to transcribe Portuguese and English audio
- **AI-Powered Summarization**: DeepSeek generates comprehensive chronological summaries with full campaign context
- **Markdown Formatting**: Automatic Obsidian-style wikilink generation for characters, locations, NPCs, and factions
- **Session Context**: Each summary includes full context from all previous sessions for narrative continuity
- **Flexible Audio Input**: Accepts any audio format (m4a, mp3, wav, etc.)
- **Transcript Caching**: Skips re-transcription if transcript already exists (faster iteration)
- **Campaign Integration**: Aggregates all session notes for cross-session consistency

---

## Quick Start

### One-Minute Setup

1. **Install dependencies**:

   ```powershell
   pip install python-dotenv openai
   ```

2. **Create `.env` file** in the project root:

   ```plaintext
   OPENAI_API_KEY=sk-...your-key-here...
   DEEPSEEK_API_KEY=sk-...your-key-here...
   ```

3. **Run the pipeline**:

   ```powershell
   python main_openai.py "C:\path\to\your\session_audio.m4a"
   ```

4. **Output** appears in `sessions/session_audio/`:
   - `transcript.txt` - Raw transcription
   - `summary.txt` - Comprehensive chronological summary
   - `summary.md` - Formatted markdown with wikilinks

---

## Prerequisites & Installation

### System Requirements

- **Python 3.8+**
- **Internet connection** (for API calls)
- Audio file in a common format (m4a, mp3, wav, ogg, etc.)

### Step 1: Install Python Packages

```powershell
pip install python-dotenv openai
```

### Step 2: Get API Keys

You'll need two API keys:

1. **OpenAI API Key** (for Whisper transcription)
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Generate an API key in Settings → API keys
   - Ensure your account has credit

2. **DeepSeek API Key** (for summarization)
   - Sign up at [platform.deepseek.com](https://platform.deepseek.com)
   - Generate an API key in your account settings
   - Ensure sufficient credits

---

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with your API keys:

```plaintext
OPENAI_API_KEY=your-openai-key-here
DEEPSEEK_API_KEY=your-deepseek-key-here
```

### Optional: Adjust Session Notes Directory

Inside [main_openai.py](main_openai.py), modify where the script looks for existing session notes:

```python
SESSION_NOTES_DIRECTORY = "C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/Finvora/Sessions"
```

### Optional: Change Transcription Model

Inside [main_openai.py](main_openai.py), switch transcription models:

```python
OPENAI_TRANSCRIPTION_MODEL = "whisper-1"  # Default
# OPENAI_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"  # Higher quality
```

---

## Main Workflow: main_openai.py

### Basic Usage

Run the script with an audio file path:

```powershell
python main_openai.py "C:\Users\Username\Downloads\session_14.m4a"
```

Or on Mac/Linux:

```bash
python main_openai.py "/Users/username/Downloads/session_14.m4a"
```

The script will:

1. Extract the filename as the session folder name
2. Create `sessions/session_name/` directory
3. Transcribe the audio (or load cached transcript)
4. Generate a comprehensive summary
5. Format as markdown with wikilinks
6. Output all three files to the session directory

### Understanding the Pipeline

The pipeline has **three stages**:

#### Stage 1: Transcription (Optional - Cached)

```
Audio File → OpenAI Whisper API → Transcript (transcript.txt)
```

**What happens:**

- Opens audio file in binary mode
- Sends to OpenAI's Whisper API with the transcription prompt
- Language set to Portuguese (`language="pt"`)
- Returns raw text transcript (30 seconds to 2 minutes typical)

**Caching:**

- If `transcript.txt` already exists, this stage is **skipped**
- Perfect for iterating on summaries without re-transcribing

**Input prompt** (from [prompts/transcription.txt](prompts/transcription.txt)):

- Campaign context: character names, NPCs, factions, locations
- D&D terminology
- Language notes

#### Stage 2: Summarization

```
Transcript + All Previous Sessions → DeepSeek API → Summary (summary.txt)
```

**What happens:**

- Loads transcript from Stage 1
- Loads all existing markdown session summaries
- Sends combined context to DeepSeek with summarization prompt
- Returns long, structured chronological summary
- Saves to `summary.txt`

**Why all previous sessions matter:**

- Maintains narrative continuity
- Allows DeepSeek to understand character and story arcs
- Clarifies faction relationships
- Provides context for NPC returning appearances

**Output format** (from [prompts/summary.txt](prompts/summary.txt)):

- Overview section with Date, Location, Participants, Main Events
- Chronological scene breakdowns (Scene, Combat, Puzzle, etc.)
- Structured tracking: NPCs, Locations, Encounters, Items, Decisions
- Clear distinction between in-game actions, speculation, and banter
- Present tense, short lines, bold/italic emphasis
- Tables, bullet lists, and code spans for clarity

#### Stage 3: Markdown Formatting & Wikilinks

```
Summary → DeepSeek API → Formatted Markdown (summary.md)
```

**What happens:**

- Takes the summary from Stage 2
- Passes previous session markdown files as context
- DeepSeek adds Obsidian-style wikilinks (`[[Link]]`) matching the style
- Preserves all content, improves readability
- Saves to `summary.md`

**Wikilink Examples:**

```markdown
The party arrives at [[Beshkarl]] where they meet [[Idagar]].
They discover a clue about the [[Silencers]].
```

**Benefits:**

- Links to other session notes in Obsidian
- Builds a knowledge graph across sessions
- Improves navigation in your D&D wiki

### Output Files

Each session creates three files in `sessions/{session_name}/`:

| File             | Purpose                                | Generated by   |
| ---------------- | -------------------------------------- | -------------- |
| `transcript.txt` | Raw audio transcription                | OpenAI Whisper |
| `summary.txt`    | Long, structured chronological summary | DeepSeek       |
| `summary.md`     | Formatted markdown with wikilinks      | DeepSeek       |

**Plus:** `combined_sessions.md` is regenerated in the project root with all session markdown combined (useful as LLM context).

---

## Project Structure

```plaintext
dnd-session-audio-recording-summary-generator/
├── main_openai.py               # Primary workflow (OpenAI transcription)
├── main.py                      # Alternative (local Whisper transcription)
├── README.md                    # This file
├── .env                         # API keys (gitignored)
├── .gitignore                   # Excludes .env and combined_sessions.md
│
├── prompts/                     # Prompt templates (customizable)
│   ├── transcription.txt        # Context for Whisper
│   ├── summary.txt              # Rules for summarization
│   └── markdown.txt             # Rules for wikilink formatting
│
├── sessions/                    # All session outputs
│   ├── session_1/
│   │   ├── transcript.txt       # Transcribed audio
│   │   ├── summary.txt          # Chronological summary
│   │   └── summary.md           # Formatted markdown
│   ├── session_2/
│   │   ├── transcript.txt
│   │   ├── summary.txt
│   │   └── summary.md
│   └── ...
│
├── combined_sessions.md         # All summaries aggregated
├── custom_prompt.py             # Utility: custom queries on transcripts
├── campaign_summary.py          # Utility: high-level campaign overview
├── join_text.py                 # Utility: rebuild combined_sessions.md
├── join_audios.py               # Utility: merge audio files
└── split_audio.py               # Utility: split audio by length
```

---

## Prompt Customization

All three LLM prompts can be customized. Edit files in the `prompts/` folder.

### prompts/transcription.txt

Controls what Whisper "sees" before transcribing.

**Good for:**

- Add new character names or NPCs
- Add faction names, location names, D&D terminology
- Change language (currently `pt` for Portuguese)
- Add pronunciation notes

### prompts/summary.txt

Controls summarization style and structure.

**Good for:**

- Level of detail (currently: comprehensive, all minor events)
- Section structure (currently: Scene, Combat, Puzzle, etc.)
- Distinction between action vs. speculation
- Output format

**Example:** Add timestamps, use emojis for combat encounters

### prompts/markdown.txt

Controls Obsidian wikilink formatting.

**Good for:**

- Aggressiveness of linking (currently: moderate)
- Naming convention for links (currently: Title Case)
- Link placement

**After editing prompts**, simply run the script again:

```powershell
python main_openai.py "C:\path\to\session.m4a"
```

---

## Advanced Usage

### Iterate on Summaries Without Re-Transcribing

Once transcript is cached:

1. Edit summary prompt in [prompts/summary.txt](prompts/summary.txt)
2. Delete `sessions/session_name/summary.txt` and `summary.md`
3. Re-run the script
4. Only summarization stages run (much faster!)

### Use Higher-Quality Transcription

For critical accuracy, edit [main_openai.py](main_openai.py):

```python
OPENAI_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"  # ~2-3x slower, higher quality
```

### Regenerate Campaign Context

Rebuild `combined_sessions.md` from all session markdown files:

```powershell
python join_text.py
```

Useful after manually editing session files.

### Custom Queries on Transcripts

Ask DeepSeek questions about specific sessions:

```powershell
python custom_prompt.py
# Prompts for session number and your question
```

### Generate Campaign Summary

Create an overview of the entire campaign:

```powershell
python campaign_summary.py
# Creates campaign_summary/output.txt
# Analyzes story arcs, character development, themes
```

### Merge Audio Files

Combine multi-part sessions:

```powershell
python join_audios.py
# Prompts for input files, outputs merged audio
```

### Split Long Audio

Break long audio into chunks:

```powershell
python split_audio.py
# Prompts for session duration or chunk size
```

---

## Other Utilities

### [main.py](main.py) - Local Whisper Transcription

Uses Whisper locally (no API calls to OpenAI needed):

```powershell
# Edit SESSION_NUMBER and AUDIO_FILE in main.py, then:
python main.py
```

**Pros**: No API costs on transcription, full offline control  
**Cons**: Requires local GPU/CPU, slower, larger dependencies

### [custom_prompt.py](custom_prompt.py) - Arbitrary Session Queries

Ask questions about specific sessions via DeepSeek.

### [campaign_summary.py](campaign_summary.py) - High-Level Campaign Overview

Generates campaign-wide analysis.

### [join_text.py](join_text.py) - Rebuild Campaign Context

Regenerates `combined_sessions.md` from all session markdown files.

### [join_audios.py](join_audios.py) & [split_audio.py](split_audio.py)

Audio processing utilities for multi-part sessions and large files.

---

## License

MIT License

## Author

Ricardo Figueiredo
