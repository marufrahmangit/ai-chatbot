# AI Chatbot (Gemini + Groq Fallback)

A simple CLI chatbot built while learning the fundamentals of working with LLM APIs — conversation memory, system prompts, temperature, rate-limit handling, and multi-provider fallback.

## What it does

- Chats with **Gemini** (`gemini-3.6-flash`) via Google's Interactions API by default
- Automatically falls back to **Groq** (`llama-3.3-70b-versatile`) if Gemini hits a rate limit
- Maintains conversation memory on both providers (server-side for Gemini, manual message history for Groq)
- Responds with a configurable personality via a system prompt

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/ai-chatbot.git
   cd ai-chatbot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and add your own API keys:
   - Get a free Gemini key at [aistudio.google.com](https://aistudio.google.com)
   - Get a free Groq key at [console.groq.com](https://console.groq.com)

## Usage

```bash
python main.py
```

Type your message and press enter. Type `Ctrl+C` to quit.

## How it works

- `ask_gemini()` sends a request to Gemini's Interactions API, using `previous_interaction_id` so the server remembers the conversation for you.
- `ask_groq()` sends a request to Groq's OpenAI-compatible API. Since Groq has no server-side memory, the full message history is built and resent manually on every call.
- If Gemini raises a `RateLimitError`, the app automatically retries with Groq instead of crashing.

## What I learned building this

- Making API calls to two different LLM providers
- System prompts vs. user prompts
- Two different approaches to conversation memory: server-managed vs. client-managed
- Temperature and how it affects response randomness
- Handling rate limits with retries
- Basic multi-provider fallback logic

## Still to explore

- Token counting
- Streaming responses
- Context window limits
- Additional generation params (`max_output_tokens`, `top_p`, etc.)