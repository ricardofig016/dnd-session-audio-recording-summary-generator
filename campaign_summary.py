import os
import time
from dotenv import load_dotenv
from openai import OpenAI


def generate_campaign_summary(deepseek_api_key):
    base_deepseek_api_url = "https://api.deepseek.com"
    deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=base_deepseek_api_url)

    # setup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sessions_dir = os.path.join(current_dir, "sessions")
    if not os.path.exists(sessions_dir):
        raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")

    session_dirs = [
        dir
        for dir in os.listdir(sessions_dir)
        if os.path.isdir(os.path.join(sessions_dir, dir))
    ]
    if not session_dirs:
        raise ValueError(f"No session directories found in: {sessions_dir}")
    session_dirs.sort()

    session_numbers = [dir.split("_")[-1] for dir in session_dirs]

    # get summaries from all sessions
    summaries = []
    for i in range(len(session_dirs)):
        session_dir = session_dirs[i]
        session_path = os.path.join(sessions_dir, session_dir)
        summary_path = os.path.join(session_path, "summary.md")

        if not os.path.exists(summary_path):
            print(f"Warning: Summary file not found for {session_dir}, skipping.")
            continue

        with open(summary_path, "r", encoding="utf-8") as file:
            summary = file.read()

        if not summary.strip():
            print(f"Warning: Summary file is empty for {session_dir}, skipping.")
            continue

        summary = f"# Session {session_numbers[i]}\n{summary.strip()}"
        summaries.append(summary)

    if not summaries:
        raise ValueError(f"No valid summaries found in: {sessions_dir}")

    # create custom prompt
    intro_prompt = "Based on the following DnD session summaries, generate a comprehensive campaign summary. Ensure the summary captures key plot points, character developments, and significant events.\n\nSession Summaries:\n"
    between_sessions_prompt = "\n\n---\n\n"
    prompt = intro_prompt + between_sessions_prompt.join(summaries)

    # send request to DeepSeek API
    print(f"Generating campaign summary for sessions: {', '.join(session_numbers)}")

    start_time = time.time()
    response = deepseek_client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    end_time = time.time()

    response_content = response.choices[0].message.content
    print(f"Request completed in {end_time - start_time:.2f} seconds.")

    return response_content


def save_response_to_file(response, filename="output.txt"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    response_dir = os.path.join(current_dir, "campaign_summary")
    os.makedirs(response_dir, exist_ok=True)

    output_path = os.path.join(response_dir, "output.txt")
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(response)

    print(f"Response saved to: {output_path}")


def main():
    load_dotenv()

    try:
        # setup DeepSeek API client
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set")

        response = generate_campaign_summary(deepseek_api_key)

        # print the response
        print("\n" + "=" * 50)
        print("API RESPONSE:")
        print("=" * 50)
        print(response)

        save_response_to_file(response)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
