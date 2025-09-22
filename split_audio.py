from pydub import AudioSegment


def split(audio_path):
    audio = AudioSegment.from_file(audio_path, format="m4a")

    midpoint = len(audio) // 2

    first_half = audio[:midpoint]
    second_half = audio[midpoint:]

    first_half.export("part1_fixed.wav", format="wav")
    second_half.export("part2_fixed.wav", format="wav")
    print(f"Audio split into part1_fixed.wav and part2_fixed.wav")


if __name__ == "__main__":
    audio_path = "C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/assets/session 5 audio.m4a"
    split(audio_path)
