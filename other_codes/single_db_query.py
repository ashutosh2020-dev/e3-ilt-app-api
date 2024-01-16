from sqlalchemy import create_engine, text


DATABASE_URL = "sqlite:///t.db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    user_cset_record = conn.execute(text(f"Drop table alembic_version"))
    print("table droped successfully")

    get_all_end_meeting_id = conn.execute(text(f"select * from Ilt_meetings where Ilt_meetings.end_at != null"))
    for mid in get_all_end_meeting_id:
        get_ilt_id = 0
        check_in = ""
