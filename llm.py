import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/")

def build_embedding_model():
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(
        model=model,
        openai_api_key=openai_api_key,
        openai_api_base=api_base,
    )

def build_chat_model(temperature: float = 0.0):
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    return ChatOpenAI(
        model=model_name,
        openai_api_key=openai_api_key,
        openai_api_base=api_base,
        temperature=temperature,
    )