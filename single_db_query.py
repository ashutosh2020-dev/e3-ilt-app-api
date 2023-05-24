from sqlalchemy import create_engine, text


DATABASE_URL = "sqlite:///t.db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    user_cset_record = conn.execute(text(f"Drop table alembic_version"))
    print("table droped successfully")
