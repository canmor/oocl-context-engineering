    
from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_markdown_documents(path: Path) -> List[Document]:
    content = path.read_text(encoding="utf-8")
    # todo: chunk it into pieces
    return []

def build_retriever_from_docs(docs: List[Document]):
    from langchain_core.vectorstores import InMemoryVectorStore
    from llm import build_embedding_model

    embedding_model = build_embedding_model()
    vector_store = InMemoryVectorStore.from_documents(
        documents=docs,
        embedding=embedding_model,
    )
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

def build_terms_retriever():
    path = Path(__file__).parent.joinpath("glossary", "terms.md")
    documents = load_markdown_documents(path)
    return build_retriever_from_docs(documents)

if __name__ == "__main__":
    from helper import run_retrieve
    run_retrieve(build_terms_retriever())