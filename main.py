import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlparse
import openai

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key and endpoint
openai.api_key = os.getenv("TOGETHER_API_KEY")
openai.api_base = "https://api.together.xyz/v1"

def extract_username_from_url(url):
    """
    Extract the Reddit username from the given Reddit profile URL.
    Example: https://www.reddit.com/user/kojied -> kojied
    """
    parsed = urlparse(url)
    if "/user/" in parsed.path:
        return parsed.path.split("/user/")[1].strip("/")
    return None

def scrape_reddit_user(username):
    """
    Scrapes the last ~300 Reddit posts and comments (max 3 pages each) for a given user.
    Filters out empty or very short text content.
    Returns a list of dictionaries with 'type' and 'content'.
    """
    headers = {'User-Agent': 'PersonaBot/1.0'}
    user_data = []
    print(f"\nScraping Reddit profile: {username}\n")

    for type_ in ['comments', 'submitted']: # Scrape both comments and posts
        after = None
        for _ in range(3):
            url = f"https://www.reddit.com/user/{username}/{type_}.json?limit=100"
            if after:
                url += f"&after={after}"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                break # Stop scraping if we hit an error
            data = resp.json()
            items = data.get('data', {}).get('children', [])
            for item in items:
                body = item['data'].get('body') or item['data'].get('selftext')
                if body and len(body.strip()) > 20:
                    user_data.append({
                        'type': type_,
                        'content': body.strip()
                    })
            after = data.get('data', {}).get('after')
            if not after:
                break # No more pages
    return user_data

def build_persona_prompt(username, items):
    """
    Constructs a detailed prompt for the LLM.
    Includes detailed instructions, citation format, and content examples.
    """
    content = ""
    for i, item in enumerate(items, 1):
        content += f"[Post #{i}] {item}\n\n"

    prompt = f"""
            You are a professional user research analyst trained in behavioral psychology and computational linguistics.

            Your task is to analyze Reddit content and generate a comprehensive and structured **User Persona** for the Reddit user `u/{username}` based on their posts and comments.

            Follow the **exact format** and instructions below. Your goal is to infer motivations, personality, and behavioral traits as realistically as possible. Where direct information is unavailable, **make reasoned assumptions** and explicitly tag them with "(assumed)".

            Cite the source **immediately after each relevant statement** using the format “(source: Post #X)”. 
            If multiple posts support a point, **list all relevant post numbers explicitly** like (source: Post #2, Post #5).
            Do not group the sources at the end.

            ---

            **User Persona for u/{username}**

            - **Age**: [Extract if possible or leave "Unknown"]
            - **Occupation**: [Extract or infer job/field/lifestyle]
            - **Relationship Status**: [Single/Married/Unknown, if implied]
            - **Location**: [Country/region/timezone if evident or implied]
            - **Tech Tier**: [Mainstream / Early Adopter / Laggard (based on tech-savviness)]
            - **Archetype**: [e.g., The Explorer / The Creator / The Seeker / The Guardian]

            **Top Traits**  
            List 4–5 distinct personality traits that emerge from the user’s tone, writing style, interests, and behavior. Avoid generic examples. Traits should reflect actual patterns seen in the data.

            ---

            **Motivations** (rate each qualitatively: High / Medium / Low)
                - Convenience:
                - Wellness:
                - Speed:
                - Preferences:
                - Comfort:
                - Dietary Needs:

            **Personality Profile**
            Indicate where they lie along each spectrum:
            - Introvert — Extrovert:
            - Intuition — Sensing:
            - Feeling — Thinking:
            - Perceiving — Judging:

            ---

            **Behaviour & Habits**
            List 3–5 bullet points summarizing behavioral patterns with citations.
            Example:
            • Orders takeaway 3–4 times a week. (source: Post #1)

            **Frustrations**
            List key annoyances or pain points mentioned or inferred, with citations.
            Example:
            • Finds it difficult to navigate restaurant menus online. (source: Post #5)

            **Goals & Needs**
            Describe what the user wants or needs, with citations.
            Example:
            • Wants to live a healthier lifestyle without giving up convenience. (source: Post #3)

            ---

            Use only the Reddit content below to draw your conclusions. Be concise, fact-based, and cite specific post numbers.

            Here are the Reddit posts and comments from u/{username}:

            {content}

            Now generate the persona using the structure above.
        """
    return prompt.strip()

def generate_persona(prompt, max_tokens=1024):
    """
    Sends the prompt to the LLM and returns the generated persona.
    """
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            top_p=0.9,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("Together.ai API call failed:", e)
        return ""

def save_persona_to_file(username, persona):
    """
    Saves the generated persona to a file.
    """
    filename = f"{username}_persona.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(persona.strip())
    print(f"Saved user persona to {filename}")

def main():
    """
    Main script flow:
    - Accepts Reddit profile URL -> Extracts username -> Scrapes posts and comments -> Builds prompt -> Calls LLM to generate persona -> Saves output to file
    """
    reddit_url = input("Enter Reddit profile URL: ").strip()
    username = extract_username_from_url(reddit_url)
    if not username:
        print("Invalid Reddit URL")
        return

    data = scrape_reddit_user(username)
    if not data:
        print("No data found on profile.")
        return

    print(f"{len(data)} items scraped from u/{username}")
    print("\nGenerating user persona...")

    prompt = build_persona_prompt(username, data)
    persona = generate_persona(prompt, max_tokens=1024)
    if persona.strip():
        save_persona_to_file(username, persona)
    else:
        print("Persona generation failed or returned empty.")

if __name__ == "__main__":
    main()
