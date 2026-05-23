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


while True:

    query=input(
        "\nAsk: "
    )

    if query.lower()=="exit":
        break


    docs=retriever.invoke(
        query
    )


    print(
        "\nRetrieved chunks:\n"
    )


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
You are an expert financial SQL assistant.

Use ONLY the schema context below.

Schema:
{context}

User Question:
{query}

Rules:

1. Use only tables present in schema
2. Use only columns present in schema
3. Never invent tables
4. Never invent columns
5. If schema lacks information say so
6. Return SQL first
7. Then explain briefly
"""


    response=llm.invoke(
        prompt
    )


    print(
        "\n========== RESPONSE ==========\n"
    )

    print(
        response.content
    )