from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///ilt_db.db"
# query = "ALTER TABLE meeting_issue_mapping ADD parent_issue_id INT NULL DEFAULT NULL;"
# query = "ALTER TABLE meeting_issue_mapping MODIFY  parent_meeting_responce_id INT NOT NULL;"
query = """
        ALTER TABLE meeting_issue_mapping
        ADD FOREIGN KEY (parent_meeting_response_id) REFERENCES meeting_response (id)
        """

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    user_cset_record = conn.execute(text(query))
    for i in user_cset_record:
        print(i)
print("success")