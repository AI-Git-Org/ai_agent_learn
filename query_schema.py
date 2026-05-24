import os

from dotenv import load_dotenv

from pinecone import Pinecone

from google import genai


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


gemini_client=genai.Client(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)



def get_query_embedding(text):

    response=pc.inference.embed(
        model="llama-text-embed-v2",

        inputs=[text],

        parameters={
            "input_type":"query"
        }
    )

    return response[0]["values"]



def get_gemini_response(prompt):

    response=gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text



while True:

    query=input(
        "\nAsk: "
    )

    if query.lower()=="exit":
        break


    query_embedding=get_query_embedding(
        query
    )


    results=index.query(
        vector=query_embedding,

        top_k=3,

        include_metadata=True,

        namespace="schema-v1"
    )


    context="\n".join(
        [
            match["metadata"]["text"]
            for match in results["matches"]
        ]
    )


    prompt=f"""
You are an expert financial SQL assistant.

Schema:
{context}

Question:
{query}

Rules:

1. Use only schema tables
2. Use only schema columns
3. Never invent names
4. Return SQL first
5. Then explain
"""


    response=get_gemini_response(
        prompt
    )


    print("\n")
    print(response)