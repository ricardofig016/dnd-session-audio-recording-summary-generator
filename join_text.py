import os
import pyperclip

SESSION_NOTES_DIRECTORY = "C:/Users/LENOVO/Desktop/dnd/worlds/Finvora/Finvora/Sessions"


def get_session_number(file):
    file_name = os.path.splitext(file)[0]
    session_number = float(file_name.split(" ")[1].strip())
    if session_number.is_integer():
        session_number = int(session_number)
    return session_number


def get_markdown_file_paths():
    files = {}
    for file in os.listdir(SESSION_NOTES_DIRECTORY):
        if file.lower().startswith("session") and file.endswith(".md"):
            session_number = get_session_number(file)
            files[session_number] = os.path.join(SESSION_NOTES_DIRECTORY, file)
    file_paths = [files[key] for key in sorted(files.keys())]
    return file_paths


def get_text_from_file(file):
    title = file.replace(".md", "")
    content = f"# {title}\n\n"
    with open(file, "r", encoding="utf-8") as file:
        content += file.read()
    return content


def main():
    # Gen text
    files = get_markdown_file_paths()
    text = ""
    for file in files:
        text += get_text_from_file(file) + f"\n\n{'='*40}\n\n"

    # Config
    copy = True

    # File name
    from_session = get_session_number(files[0])
    to_session = get_session_number(files[-1])

    # Copy to clipboard
    if copy:
        pyperclip.copy(text.strip())
        print("Copied to clipboard")

    # Save to output file
    output_file = "combined_sessions.md"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text.strip())
    print(f"Combined text saved to '{output_file}'")


if __name__ == "__main__":
    main()
