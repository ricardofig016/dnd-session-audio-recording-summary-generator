from pydub import AudioSegment


def join_audios(file1_path, file2_path, output_path):
    audio1 = AudioSegment.from_file(file1_path, format="m4a")
    audio2 = AudioSegment.from_file(file2_path, format="m4a")

    combined_audio = audio1 + audio2

    combined_audio.export(output_path, format="mp4")
    print(f"Combined audio saved to {output_path}")


if __name__ == "__main__":
    file1 = "part1_fixed.m4a"
    file2 = "part2_fixed.m4a"
    output = "output_audio.m4a"
    join_audios(file1, file2, output)
