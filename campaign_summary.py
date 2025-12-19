import os
import time
from dotenv import load_dotenv
from openai import OpenAI


def generate_campaign_summary(deepseek_api_key):
    base_deepseek_api_url = "https://api.deepseek.com"
    deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=base_deepseek_api_url)

    # setup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    combined_sessions_path = os.path.join(current_dir, "combined_sessions.md")
    if not os.path.exists(combined_sessions_path):
        raise FileNotFoundError(
            f"Combined sessions file not found: {combined_sessions_path}"
        )

    with open(combined_sessions_path, "r", encoding="utf-8") as file:
        combined_sessions_content = file.read()

    if not combined_sessions_content.strip():
        raise ValueError(f"Combined sessions file is empty: {combined_sessions_path}")

    # create custom prompt using the precompiled combined sessions file
    intro_prompt = (
        "Based on the following DnD session summaries, generate a comprehensive "
        "campaign summary. Ensure the summary captures key plot points, character "
        "developments, and significant events.\n\nSession Summaries:\n"
    )
    prompt = intro_prompt + combined_sessions_content.strip()

    # send request to DeepSeek API
    print("Generating campaign summary from combined_sessions.md")

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
