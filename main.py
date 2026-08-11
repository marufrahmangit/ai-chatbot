from google import genai
from google.genai._gaos.lib.compat_errors import RateLimitError, APIError as InteractionAPIError
from groq import Groq
from dotenv import load_dotenv
import os
import time
import re

load_dotenv()

max_retries = 3


def ask_gemini(user_input, previous_id):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=user_input,
                system_instruction="You are a professor. Always respond in professor speak, regardless of what the user asks but answer in short.",
                generation_config={"temperature":0},
                previous_interaction_id=previous_id
            )
    return interaction.output_text, interaction.id

def ask_groq(user_input, message_history):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    message_history.append({"role": "user", "content": user_input})
    
    chat_completion = client.chat.completions.create(
        messages=message_history,
        model="llama-3.3-70b-versatile",
    )
    
    reply = chat_completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply})
    
    return reply, message_history

previous_id = None
message_history = []

while True:
    user_input = input("You: ")
    try:
        reply, previous_id = ask_gemini(user_input, previous_id)
        print("Bot (Gemini):", reply)
    except RateLimitError:
        print("Gemini rate-limited, falling back to Groq...")
        reply, message_history = ask_groq(user_input, message_history)
        print("Bot (Groq):", reply)
