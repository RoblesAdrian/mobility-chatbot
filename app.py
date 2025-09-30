from fastapi import FastAPI, Request
from llm import ask_ollama
from db import run_sql_query
from prompt_templates import SQL_PROMPT_TEMPLATE, RESPONSE_PROMPT_TEMPLATE

from sqlalchemy import create_engine
import json

engine = create_engine("sqlite:///mobility.db")

app = FastAPI()

TABLE_SCHEMA = """
Table: vehicles
- id (int)
- name (text)
- status (text)
- last_service_date (date)
- mileage (int)

Table: trips
- id (int)
- vehicle_id (int)
- start_time (datetime)
- end_time (datetime)
- distance_km (float)
"""

@app.post("/query")
async def query_nl(request: Request):
    data = await request.json()
    user_question = data["question"]

    # Step 1: Generate SQL from question
    sql_prompt = SQL_PROMPT_TEMPLATE.format(
        schema=TABLE_SCHEMA,
        question=user_question
    )
    sql_query = ask_ollama(sql_prompt).strip()

    if sql_query.startswith("```sql"):
        sql_query = sql_query.removeprefix("```sql").strip()
    if sql_query.endswith("```"):
        sql_query = sql_query.removesuffix("```").strip()

    print(f"[DEBUG] Generated SQL: {sql_query}")

    # Step 2: Run SQL
    try:
        results = run_sql_query(sql_query)
    except Exception as e:
        return {"error": str(e), "sql": sql_query}

    # Step 3: Generate natural language answer
    results_json = json.dumps(results, indent=2)
    response_prompt = RESPONSE_PROMPT_TEMPLATE.format(
        question=user_question,
        sql=sql_query,
        results=results_json
    )
    response_text = ask_ollama(response_prompt).strip()

    return {
        "sql": sql_query,
        "results": results,
        "response": response_text
    }
