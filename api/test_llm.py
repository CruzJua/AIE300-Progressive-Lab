import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "What is Docker in one sentence?"}
    ]
)
print(message.content[0].text)