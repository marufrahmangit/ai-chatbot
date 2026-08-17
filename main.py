from google import genai
from google.genai._gaos.lib.compat_errors import RateLimitError, APIError as InteractionAPIError
from groq import Groq
from dotenv import load_dotenv
import os
import time
import re

load_dotenv()

SYSTEM_PROMPT = '''
You are a helpful assistant and your name is "Jarvis" 
and you only start responding once your name is said. 
Answer clearly and concisely, address me as "Sir".
'''

def ask_gemini(user_input, previous_id, max_retries=2):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    last_error = None

    for attempt in range(max_retries):
        try:
            stream = client.interactions.create(
                model="gemini-3.6-flash",
                input=user_input,
                system_instruction=SYSTEM_PROMPT,
                generation_config={"temperature": 0},
                previous_interaction_id=previous_id,
                stream=True,
            )

            full_reply = ""
            new_id = None
            print("Bot (Gemini):", end=" ", flush=True)
            for event in stream:
                if event.event_type == "step.delta" and event.delta.type == "text":
                    print(event.delta.text, end="", flush=True)
                    full_reply += event.delta.text
                elif event.event_type == "interaction.completed":
                    new_id = event.interaction.id
            print()

            return full_reply, new_id

        except RateLimitError as e:
            last_error = e
            match = re.search(r"retry in ([\d.]+)s", e.message)
            wait_time = float(match.group(1)) if match else 3
            print(f"Gemini rate-limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

    raise last_error

def ask_groq(user_input, message_history, max_retries=2):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"), max_retries=max_retries)

    if not message_history:
        message_history.append({"role": "system", "content": SYSTEM_PROMPT})

    message_history.append({"role": "user", "content": user_input})

    chat_completion = client.chat.completions.create(
        messages=message_history,
        model="llama-3.3-70b-versatile",
        temperature=0,
        stream=True,
    )

    full_reply = ""
    print("Bot (Groq):", end=" ", flush=True)
    for chunk in chat_completion:
        piece = chunk.choices[0].delta.content
        if piece:
            print(piece, end="", flush=True)
            full_reply += piece
    print()

    message_history.append({"role": "assistant", "content": full_reply})

    return full_reply, message_history

previous_id = None
message_history = []
full_history = []
use_groq = False

while True:
    user_input = input("You: ")
    if not use_groq:
        try:
            reply, previous_id = ask_gemini(user_input, previous_id)
            full_history.append({"role": "user", "content": user_input})
            full_history.append({"role": "assistant", "content": reply})
            continue
        except RateLimitError:
            print("Gemini rate-limited, falling back to Groq for the rest of this session...")
            use_groq = True
            message_history = [{"role": "system", "content": SYSTEM_PROMPT}] + full_history

    reply, message_history = ask_groq(user_input, message_history)
    full_history.append({"role": "user", "content": user_input})
    full_history.append({"role": "assistant", "content": reply})