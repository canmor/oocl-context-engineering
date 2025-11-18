from langchain_core.prompts import ChatPromptTemplate
from qa import chat

class RAG:
    def __init__(self, context: str | None = None, retriever = None):
        self.context = context
        self.retriever = retriever

    def query(self, question: str):
        if self.context is None:
            sources = self.retriever.invoke(question)
            self.context = "\n\n".join([doc.page_content for doc in sources])

        prompt_template = ChatPromptTemplate.from_messages([
            # todo: enhance system prompt
            ("system", """
             You are an AI assistant that helps people find information.
             """),
            ("user", "question: {messages}\n\ncontext: {context}"),
        ])
        prompt = prompt_template.format_messages(messages=question, context=self.context)
        return chat(prompt=prompt)