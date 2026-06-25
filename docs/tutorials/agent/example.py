import os
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("OPENAI_API_BASE"),
)

stream = client.chat.completions.create(
  model="google/gemma-4-26b-a4b-it",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ],
  stream=True,
  stream_options={"include_usage": True},
)

usage = None
for chunk in stream:
    if chunk.choices:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    # The final chunk carries the aggregate usage when include_usage is set.
    if getattr(chunk, "usage", None):
        usage = chunk.usage

print()

if usage:
    # Pricing in USD per 1M tokens.
    PRICE_PER_1M_PROMPT = 0.123
    PRICE_PER_1M_COMPLETION = 0.454

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    prompt_cost = prompt_tokens * PRICE_PER_1M_PROMPT / 1_000_000
    completion_cost = completion_tokens * PRICE_PER_1M_COMPLETION / 1_000_000
    total_cost = prompt_cost + completion_cost

    print()
    print("──── telemetry ────")
    print(f"prompt     : {prompt_tokens:>8} tokens")
    print(f"completion : {completion_tokens:>8} tokens")
    print(f"total      : {total_tokens:>8} tokens")
    print(f"cost       : ${total_cost:.6f}")
else:
    print("[telemetry] no usage returned by the endpoint")
