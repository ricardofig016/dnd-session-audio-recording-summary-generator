from pydub import AudioSegment


def split(audio_path):
    audio = AudioSegment.from_file(audio_path, format="m4a")

    forth_time = len(audio) // 4

    first = audio[:forth_time]
    second = audio[forth_time : 2 * forth_time]
    third = audio[2 * forth_time : 3 * forth_time]
    forth = audio[3 * forth_time :]

    first.export("part1_fixed.wav", format="wav")
    second.export("part2_fixed.wav", format="wav")
    third.export("part3_fixed.wav", format="wav")
    forth.export("part4_fixed.wav", format="wav")
    print(f"Audio split into 4 parts")


if __name__ == "__main__":
    audio_path = "C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/assets/session 5 audio.m4a"
    split(audio_path)
