# Reddit-Persona-Extractor
A prompt-engineered Reddit persona generator that scrapes user content and builds detailed, cited personality profiles using open-source LLMs.

## What It Does
- Scrapes recent posts and comments from a Reddit user.
- Builds a custom prompt with behavioral and psychological cues.
- Uses a local LLM (like Mistral) to generate a structured persona with:
    - Age, Occupation, Personality Type, Archetype, etc.
    - Traits, Motivations, Habits, Goals, and Frustrations.
    - Inline source citations from specific Reddit posts.
 
## How to Run
1. Clone the repository
   ```bash
   git clone https://github.com/your-username/reddit-persona-extractor.git
   cd reddit-persona-extractor

2. Install dependencies
   ```bash
   pip install -r requirements.txt

3. Setup Environment Variables
    - Create a .env file in the root directory:
    ```bash
    touch .env
    ```
    - Add your Together API key:
    ```bash
     TOGETHER_API_KEY=your_together_api_key_here
    ```
    - Get Your Together API Key
      1. Go to https://together.ai
      2. Create an account or log in
      3. Visit the API Keys section in your dashboard
      4. Click "Create API Key"
      5. Copy and paste the key into your .env file as shown above

4. Run the script
   ```bash
   python main.py
   ```
    When prompted, enter the Reddit profile URL (e.g.):
    ```
    https://www.reddit.com/user/kojied
    ```

## Why Together API?
Instead of downloading large open-source models (e.g. Mistral-7B) locally, this project uses the Together.ai API to run them in the cloud. This offers several advantages:
- No need to store multi-GB model weights on your system
- Faster inference using Together’s optimized infrastructure
- Runs on any machine – even low-resource laptops
- Access to a range of state-of-the-art open-source models on demand
