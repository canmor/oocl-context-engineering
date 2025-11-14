from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url=os.getenv("OPENAI_API_BASE"),
  api_key=os.getenv("OPENAI_API_KEY"),
)

embedding = client.embeddings.create(
  model="openai/text-embedding-3-small",
  input="Your text string goes here",
  encoding_format="float"
)

if len(embedding.data) > 0:
  print("✅Congratulations! Embedding created successfully.")
else:
  print("❌Failed to create embedding, please check your configuration.")