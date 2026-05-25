import os
import uuid

from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

load_dotenv()


pc=Pinecone(
    api_key=os.getenv(
        "PINECONE_API_KEY"
    )
)

index=pc.Index(
    os.getenv(
        "PINECONE_INDEX"
    )
)


docs=[]

for i in range(1,7):

    filename=f"doc{i}.txt"

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        docs.append(
            f.read()
        )


splitter=RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


chunks=[]

for doc in docs:

    chunks.extend(
        splitter.split_text(
            doc
        )
    )


print(
    f"Total chunks: {len(chunks)}"
)


vectors=[]


for i,chunk in enumerate(chunks):

    response=pc.inference.embed(
        model="llama-text-embed-v2",

        inputs=[chunk],

        parameters={
            "input_type":"passage"
        }
    )

    embedding=response[0]["values"]

    vectors.append(
        {
            "id":str(uuid.uuid4()),

            "values":embedding,

            "metadata":{
                "chunk_id":i,
                "text":chunk
            }
        }
    )


index.upsert(
    vectors=vectors,
    namespace="schema-v1"
)


print(
    "Embeddings stored"
)