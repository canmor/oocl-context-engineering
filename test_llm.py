import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  base_url=os.getenv("OPENAI_API_BASE"),
  api_key=os.getenv("OPENAI_API_KEY"),
)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)

if len(response.choices) > 0:
    print("✅Congratulations! LLM response created successfully.")
    print(response.choices[0].message.content)
else:
    print("❌Failed to create LLM response, please check your configuration.")