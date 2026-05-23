import os

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_pinecone import (
    PineconeVectorStore
)


load_dotenv()


embeddings=GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
    task_type="retrieval_query",
    output_dimensionality=1024
)


vector_store=PineconeVectorStore(
    index_name=os.getenv(
        "PINECONE_INDEX"
    ),
    embedding=embeddings
)


retriever=vector_store.as_retriever(
    search_kwargs={
        "k":3
    }
)


llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


query=input("Ask: ")


docs=retriever.invoke(
    query
)


print("\nRetrieved:\n")

for d in docs:
    print(
        d.metadata
    )


context="\n".join(
    [
        doc.page_content
        for doc in docs
    ]
)


prompt=f"""
You are a financial SQL assistant.

Use ONLY this schema context.

Schema:
{context}

Question:
{query}

Generate:
1. SQL query
2. Explanation
"""


response=llm.invoke(
    prompt
)


print("\n")
print(
    response.content
)