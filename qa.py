from llm import build_chat_model

def chat(prompt: str):
    model = build_chat_model(temperature=0.0)
    return model.invoke(prompt)

if __name__ == "__main__":
    chat(input("Please enter your question: ")).pretty_print()