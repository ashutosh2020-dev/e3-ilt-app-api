from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///ilt_db.db"
# query = "ALTER TABLE meeting_issue_mapping ADD parent_issue_id INT NULL DEFAULT NULL;"
# query = "ALTER TABLE meeting_issue_mapping MODIFY  parent_meeting_responce_id INT NOT NULL;"
# query = """ALTER TABLE meeting_issue_mapping ADD FOREIGN KEY (parent_meeting_response_id) REFERENCES meeting_response (id)"""
# query = """ ALTER TABLE ilt_to_do_task DROP parent_to_do_id;"""
# query = """ ALTER TABLE ilt_to_do_task ADD parent_to_do_id INT NULL DEFAULT NULL;"""
# query = """ ALTER TABLE Ilt_to_do_task ADD created_at DATETIME NULL; """
# query = """ CREATE TABLE Ilt_whiteboard (id INT AUTO_INCREMENT PRIMARY KEY,description LONGTEXT,iltId INT NOT NULL,FOREIGN KEY (iltId) REFERENCES Ilts(id));"""
# query = """ ALTER TABLE Ilt_meetings ADD CONSTRAINT fk_note_taker_id FOREIGN KEY (note_taker_id) REFERENCES users(id);"""
# query = """ ALTER TABLE Ilt_meetings ADD COLUMN note_taker_id INT NULL DEFAULT NULL;"""
# ALTER TABLE ilt_meeting_response_mapping ADD is_active boolean NULL DEFAULT true;
# ALTER TABLE ilt_meeting_response_mapping MODIFY is_active boolean NOT NULL default true;
# ALTER TABLE Ilt_members_maping ADD is_active boolean NOT NULL DEFAULT true;
# ALTER TABLE Ilt_members_maping ALTER COLUMN is_active SET DEFAULT true;
# CREATE INDEX idx_is_active ON Ilt_members_maping (is_active);
# -- ALTER TABLE meeting_response MODIFY feedback text NULL default null;
# -- ALTER TABLE meeting_response MODIFY notes text NULL default null;
# -- ALTER TABLE Ilt_rocks MODIFY description text NOT NULL;
# -- ALTER TABLE Ilt_to_do_task MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_updates MODIFY description text NOT NULL;
# -- ALTER TABLE issue MODIFY issue text NOT NULL;
# -- ALTER TABLE Ilt_priorities MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_updates MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_response MODIFY notes text NULL default null;
# -- ALTER TABLE Ilt_rocks MODIFY description text NOT NULL;
# -- ALTER TABLE Ilt_to_do_task MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_updates MODIFY description text NOT NULL;
# -- ALTER TABLE issue MODIFY issue text NOT NULL;
# -- ALTER TABLE Ilt_priorities MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_updates MODIFY description text NOT NULL;
# -- ALTER TABLE meeting_response DROP rockName;
# -- ALTER TABLE meeting_response DROP onTrack;
# -- drop table meeting_issue_mapping;
# -- drop table Ilt_issue_priorities_mapping;
# -- drop table issue;
# -- ALTER TABLE meeting_response MODIFY checkin_professional_best text NULL default null;

query = """
  ALTER TABLE ilt_meeting_response_mapping ADD CONSTRAINT uq_ilt__mapping UNIQUE('meeting_user_id',  'meeting_user_id');
        """
## meeting_note_taker_id  INT NULL DEFAULT NULL;

# query2= """
#         ALTER TABLE ilt_to_do_task ADD parent_to_do_id INT NULL DEFAULT NULL;
#         """

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    user_cset_record = conn.execute(text(query))
#     for i in user_cset_record:
#         print(i)
print("success")