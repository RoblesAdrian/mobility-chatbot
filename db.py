from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///mobility.db")

def run_sql_query(sql: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
