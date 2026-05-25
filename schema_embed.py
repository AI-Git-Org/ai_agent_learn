import os
import uuid
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

docs = []

for i in range(1, 7):
    filename = f"doc{i}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            t_name = data.get('table_name', 'Unknown')

            # Structured string for better embedding quality
            formatted_content = f"""
            Table: {t_name}
            Summary: {data.get('summary')}
            Columns: {json.dumps(data.get('columns'))}
            Relationships: {json.dumps(data.get('relationships'))}
            """
            # Store as tuple to keep table name linked to text
            docs.append((t_name, formatted_content))
    except FileNotFoundError:
        continue

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

vectors = []
for table_name, text in docs:
    chunks = splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        response = pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[chunk],
            parameters={"input_type": "passage"}
        )

        vectors.append({
            "id": str(uuid.uuid4()),
            "values": response[0]["values"],
            "metadata": {
                "text": chunk,
                "table": table_name # Useful for memory context
            }
        })

index.upsert(vectors=vectors, namespace="schema-v1")
print(f"Stored {len(vectors)} vectors with table metadata.")