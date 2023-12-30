# middle-ILT-app-api

### structure

<pre>
app/
├── config/
│ ├── app_settings.py
│ └── database.py
├── models.py
├── Exceptions/
| ├── CustomException.py
├── routers/
│ ├── ilt_maintenance.py
│ ├── ilt_meeting_maintenance.py
| └── user_maintenance.py
├── schemas/
│ ├── meeting_response.py  
├── services/
│ ├── ilt_service.py
│ └── ilt_meeting_service.py
└── utils.py
|main.py
|Dockerfile

</pre>

## RUN app locally
- python -B -m uvicorn main:app --host 0.0.0.0 --port 80 --reload
- uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile certs/private.key --ssl-certfile certs/certificate.crt

### Run these two commands docker cmd in root dir/path

- docker build -t middle_ilt_app1 -f Dockerfile .
- docker run -p 443:443 middle_ilt_app

### for migration

- alembic revision -m "add crete_by_me column in mdlilts"
- alembic upgrade head

### creating dummy user guide

- first create role for admin

- create admin user

- create schools

- create roles for facilitator and member

### SQL queries


- add column - ALTER TABLE ilt_meeting_response_mapping ADD is_active boolean NOT NULL;
- modify column - ALTER TABLE users MODIFY number bigint NULL default null;
- rename column-  ALTER TABLE users RENAME COLUMN saltKey to salt_key;
- drop table - drop table Ilt_to_do_mapping;
- delete specific rows - DELETE FROM Ilt_to_do_mapping WHERE id IN (17, 21, 22, 23);
- delete with specific condition - DELETE FROM Ilt_to_do_mapping
    WHERE id IN ( SELECT id FROM Ilt_to_do_mapping GROUP BY parent_to_do_id, user_id HAVING COUNT(parent_to_do_id) > 1 AND COUNT(user_id) > 1);
- adding constraint - ALTER TABLE  Ilt_to_do_mapping ADD CONSTRAINT cons_unq_parentTodo_userId UNIQUE (parent_to_do_id, user_id);