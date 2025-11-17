from llm import build_chat_model

model = build_chat_model(temperature=0.0)
query = input("Please enter your question: ")
model.invoke(query).pretty_print()