# AI Chatbot (Gemini + Groq Fallback)

A simple CLI chatbot built while learning the fundamentals of working with LLM APIs — conversation memory, system prompts, temperature, streaming, rate-limit handling, and multi-provider fallback.

## What it does

- Chats with **Gemini** (`gemini-3.6-flash`) via Google's Interactions API by default, streaming the response live as it's generated
- Automatically falls back to **Groq** (`llama-3.3-70b-versatile`, also streamed) if Gemini hits a rate limit
- Maintains conversation memory on both providers (server-side for Gemini, manual message history for Groq), and carries the conversation over to Groq if a mid-session fallback happens
- Responds as "Jarvis," a configurable personality set via a system prompt on both providers

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

- `ask_gemini()` sends a request to Gemini's Interactions API, using `previous_interaction_id` so the server remembers the conversation for you. Both providers use the same system prompt for a consistent personality.
- On a 429, it doesn't guess a backoff time. It parses the exact `retry in Xs` value from Gemini's own error message and sleeps for that long before retrying, up to `max_retries` attempts.
- If Gemini's retries are exhausted, the app switches to Groq and stays there for the rest of the session (a "sticky" fallback), instead of re-testing Gemini on every message.
- `ask_groq()` sends a request to Groq's OpenAI-compatible API. Since Groq has no server-side memory, the full message history is built and resent manually on every call. Groq also has a built-in `max_retries` option on its client for its own transient errors.

## Known limitations

- **No shared memory across providers.** If the app falls back to Groq mid-conversation, Groq starts with no knowledge of what was said to Gemini. This is a real gap, not yet fixed.
- **Sticky fallback doesn't reset.** Once Gemini fails, it's not retried again for the rest of the session, even if the rate limit would have cleared. Simpler to reason about, but not the most "correct" behavior.

## What I learned building this

- Making API calls to two different LLM providers
- System prompts vs. user prompts, and how each API expects them (a dedicated param on Gemini, a `role: "system"` message on Groq)
- Two different approaches to conversation memory: server-managed vs. client-managed
- Temperature and how it affects response randomness
- Reading a provider's actual error message instead of guessing (parsing Gemini's real retry-after time rather than blind exponential backoff)
- Digging into an SDK's source code when the public docs and the actual exception hierarchy don't match
- Basic multi-provider fallback logic, including the tradeoffs of making it sticky

## Still to explore

- Token counting
- Streaming responses
- Context window limits
- Additional generation params (`max_output_tokens`, `top_p`, etc.)
- Carrying conversation history over when falling back mid-conversation