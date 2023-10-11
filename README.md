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
- python -B -m uvicorn main:app --host 0.0.0.0 --port 80 
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
