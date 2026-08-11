from google import genai
from google.genai._gaos.lib.compat_errors import RateLimitError, APIError as InteractionAPIError
from groq import Groq
from dotenv import load_dotenv
import os
import time
import re

load_dotenv()

def ask_gemini(user_input, previous_id, max_retries=2):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    last_error = None

    for attempt in range(max_retries):
        try:
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=user_input,
                system_instruction="You are a professor. Always respond in professor speak, regardless of what the user asks but answer in short.",
                generation_config={"temperature": 0},
                previous_interaction_id=previous_id
            )
            return interaction.output_text, interaction.id
        except RateLimitError as e:
            last_error = e
            match = re.search(r"retry in ([\d.]+)s", e.message)
            wait_time = float(match.group(1)) if match else 5
            print(f"Gemini rate-limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
    
    raise last_error  # re-raise the real, already-built exception

def ask_groq(user_input, message_history, max_retries=2):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"), max_retries=max_retries)

    if not message_history:
        message_history.append({
            "role": "system",
            "content": "You are a professor. Always respond in professor speak, regardless of what the user asks but answer in short."
    })
    
    message_history.append({"role": "user", "content": user_input})
    
    chat_completion = client.chat.completions.create(
        messages=message_history,
        model="llama-3.3-70b-versatile",
        temperature=0,
    )
    
    reply = chat_completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply})
    
    return reply, message_history

previous_id = None
message_history = []
use_groq = False # sticky switch — once True, stop bothering Gemini

while True:
    user_input = input("You: ")
    if not use_groq:
        try:
            reply, previous_id = ask_gemini(user_input, previous_id)
            print("Bot (Gemini):", reply)
            continue
        except RateLimitError:
            print("Gemini rate-limited, falling back to Groq for the rest of this session...")
            use_groq = True
    reply, message_history = ask_groq(user_input, message_history)
    print("Bot (Groq):", reply)
