
def run_retrieve(retriever):
    results = retriever.invoke(input("Enter your query: "))
    for doc in results:
        print(f"Source: {doc.metadata['source']}, Chunk: {doc.metadata.get('chunk', 'N/A')}\n{doc.page_content}\n")
