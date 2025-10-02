import os
import time
from dotenv import load_dotenv
from openai import OpenAI


def send_custom_prompt_request(session_number, custom_prompt, deepseek_api_key):
    base_deepseek_api_url = "https://api.deepseek.com"
    deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=base_deepseek_api_url)

    # get transcript from session
    current_dir = os.path.dirname(os.path.abspath(__file__))
    session_directory = os.path.join(current_dir, f"sessions/session_{session_number}")
    transcript_path = os.path.join(session_directory, "transcript.txt")

    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

    with open(transcript_path, "r", encoding="utf-8") as file:
        transcript = file.read()

    if not transcript.strip():
        raise ValueError(f"Transcript file is empty: {transcript_path}")

    print(f"Sending custom prompt request for session {session_number}...")

    # Send request to DeepSeek API
    start_time = time.time()
    response = deepseek_client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": f"{custom_prompt}\n\nAnswer the prompt according to the following dnd session transcript:\n{transcript}",
            },
        ],
        stream=False,
    )

    response_content = response.choices[0].message.content
    end_time = time.time()
    print(f"Request completed in {end_time - start_time:.2f} seconds.")

    return response_content


def main():
    load_dotenv()

    try:
        # setup DeepSeek API client
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set")

        # input
        session_number = input("Enter session number: ").strip()
        print("Enter your custom prompt (press Enter twice to finish):")

        custom_prompt_lines = []
        while True:
            line = input()
            if line == "":
                break
            custom_prompt_lines.append(line)

        custom_prompt = "\n".join(custom_prompt_lines)

        if not custom_prompt.strip():
            print("Error: Custom prompt cannot be empty")
            return

        response = send_custom_prompt_request(
            session_number,
            custom_prompt,
            deepseek_api_key,
        )

        print("\n" + "=" * 50)
        print("API RESPONSE:")
        print("=" * 50)
        print(response)

        # save the response
        current_dir = os.path.dirname(os.path.abspath(__file__))
        response_directory = os.path.join(current_dir, "custom_prompt")
        os.makedirs(response_directory, exist_ok=True)

        output_path = os.path.join(response_directory, "output.txt")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(f"Custom Prompt:\n{custom_prompt}\n\n")
            file.write(f"Response:\n{response}")

        print(f"Response saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
