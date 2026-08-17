# testing chat streaming using Groq

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
    print()  # newline once the stream finishes

    message_history.append({"role": "assistant", "content": full_reply})

    return full_reply, message_history

message_history = []
full_history = []   # provider-agnostic transcript, kept regardless of who's answering

while True:
    user_input = input("You: ")
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}] + full_history
    reply, message_history = ask_groq(user_input, message_history)

    full_history.append({"role": "user", "content": user_input})
    full_history.append({"role": "assistant", "content": reply})