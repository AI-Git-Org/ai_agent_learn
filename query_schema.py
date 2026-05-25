import os
import mysql.connector
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

load_dotenv()

# --- Configuration ---
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database Credentials from your connection.py
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Dbroot123$",
    "database": "financial_db"
}

def run_sql_query(sql):
    """Executes the LLM-generated SQL against MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            return {"columns": [], "data": [], "message": "No results found."}

        columns = list(rows[0].keys())
        data = [list(row.values()) for row in rows]

        conn.close()
        return {"columns": columns, "data": data}
    except mysql.connector.Error as err:
        return {"error": str(err)}

# --- LLM Instructions ---
# We emphasize the exact table names from your init.sql
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are an expert financial SQL assistant. "
        "You must use the EXACT casing provided in the schema context. "
        "Output ONLY valid SQL in the first step, then explain results in the second."
    )
}

chat_history = []
WINDOW_SIZE = 3

def get_query_embedding(text):
    # Matches your schema_embed.py model
    response = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=[text],
        parameters={"input_type": "query"}
    )
    return response[0]["values"]

while True:
    query = input("\nAsk (or 'exit'): ")
    if query.lower() == "exit":
        break

    # 1. RAG: Retrieve Schema
    query_embedding = get_query_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        namespace="schema-v1"
    )
    schema_context = "\n---\n".join([match["metadata"]["text"] for match in results["matches"]])

    # 2. Phase 1: Generate SQL
    sql_gen_prompt = f"Schema Context:\n{schema_context}\n\nQuestion: {query}\n\nReturn ONLY the SQL code block."

    messages = [SYSTEM_MESSAGE] + chat_history[-(WINDOW_SIZE * 2):] + [{"role": "user", "content": sql_gen_prompt}]

    try:
        res = client.chat.completions.create(model="gpt-4o", messages=messages)
        # Extract SQL from markdown blocks
        generated_sql = res.choices[0].message.content.replace("```sql", "").replace("```", "").strip()

        print(f"\n[Generated SQL]:\n{generated_sql}")

        # 3. DB Execution
        db_results = run_sql_query(generated_sql)

        if "error" in db_results:
            print(f"SQL Error: {db_results['error']}")
            continue

        # 4. Phase 2: Analyze Results
        final_prompt = f"The database returned: {db_results}. \n\nOriginal Question: {query}. Provide the final answer."

        # Build message history for the final summary
        summary_messages = messages + [
            {"role": "assistant", "content": generated_sql},
            {"role": "user", "content": final_prompt}
        ]

        final_res = client.chat.completions.create(model="gpt-4o", messages=summary_messages)
        answer = final_res.choices[0].message.content

        print(f"\n[Answer]:\n{answer}")

        # Update History with a clean summary for the sliding window
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": answer})

    except Exception as e:
        print(f"Error: {e}")