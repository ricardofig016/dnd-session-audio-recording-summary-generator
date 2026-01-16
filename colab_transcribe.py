# !pip install openai-whisper
# !apt-get update -y
# !apt-get install -y ffmpeg
# !ffmpeg -version

import os
import time
import whisper

CURRENT_DIRECTORY = "./"
AUDIO_FILE = "./session13.m4a"  # CHANGE THIS
WHISPER_MODEL = "turbo"  # turbo for best results, small for faster results
TRANSCRIPT_FILE_NAME = "transcript.txt"

INITIAL_PROMPT = """
    This is a Dungeons & Dragons 5th Edition 2024 live play session. The DM narrates the story, and four players roleplay their characters.
    
    Main Characters (full name / nickname): Aranith Eanobra / Ara (tiefling paladin), Elowen Fernwyn / Fern (wood elf monk), Freya Moondancer / Freya (high elf lore bard), Kael Raval / Kael (half elf arcane trickster rogue).
    
    Companion NPCs: Alice (half-elf knight), Meilavan (human wizard).
    
    NPCs and Factions: Thorkell (Blood Order mentor), Magnus (elderly wizard), Velastra (blue tiefling sorcerer, antagonist), the Silencers (assassin faction), the Blood Order (thieves' guild), Jorni (gnome mine receptionist), Idagar (centaur bartender).
    
    Key Locations: Evarnia, Beshkarl (Low City and High City), Fort of Iraaki, Dark Continent.
    
    Technical Terms: Saving Throw, Check, Short Rest, Long Rest, Hit Points (HP), Armor Class (AC), Inspiration, Attunement, Divine Sense, Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma, Acrobatics, Animal Handling, Arcana, Athletics, Deception, History, Insight, Intimidation, Investigation, Medicine, Nature, Perception, Performance, Persuasion, Religion, Sleight of Hand, Stealth, Survival.
    
    Expect character voices, game mechanics discussion, and mixed in-character roleplay with out-of-character banter. The speakers code-switch between English and Portuguese, with Portuguese being the main language. Transcribe all dialogue as spoken without translation. 
    """


# Transcribe audio using Whisper
def transcribe_audio():
    print("Transcribing audio...")
    model = whisper.load_model(WHISPER_MODEL)

    start_time = time.time()
    result = model.transcribe(
        audio=AUDIO_FILE,
        verbose=True,
        # initial_prompt=INITIAL_PROMPT,
        # carry_initial_prompt=True,
    )

    end_time = time.time()
    print(f"Transcription completed in { end_time - start_time:.2f} seconds.")

    transcript_path = os.path.join(CURRENT_DIRECTORY, TRANSCRIPT_FILE_NAME)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(result["text"])

    return result["text"]


# Main pipeline
def main():
    transcript = None
    transcript_path = os.path.join(CURRENT_DIRECTORY, TRANSCRIPT_FILE_NAME)
    transcript = transcribe_audio()


if __name__ == "__main__":
    main()
