import os
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from langchain_pinecone import (
    PineconeVectorStore
)

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)

from langchain.schema import Document


load_dotenv()


PINECONE_API_KEY=os.getenv(
    "PINECONE_API_KEY"
)

INDEX_NAME=os.getenv(
    "PINECONE_INDEX"
)


pc=Pinecone(
    api_key=PINECONE_API_KEY
)


if INDEX_NAME not in pc.list_indexes().names():

    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,
        metric="cosine",

        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    print("Created index")


embeddings=GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
    task_type="retrieval_document",
    output_dimensionality=1024
)


docs=[]

for i in range(1,7):

    filename=f"doc{i}.txt"

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        text=f.read()

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source":filename
                }
            )
        )


splitter=RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


chunks=splitter.split_documents(
    docs
)

print(
    f"Total chunks: {len(chunks)}"
)


vector_store=PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=INDEX_NAME
)


print(
    "Embeddings stored in Pinecone"
)