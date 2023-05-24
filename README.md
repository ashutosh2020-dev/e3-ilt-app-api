# middle-ILT-app-api-code

# structure
app/
├── config/
│   ├── app_settings.py
│   └── database.py
├── models.py
├── routers/
│   ├── ilt_maintenance.py
│   ├── ilt_meeting_maitenance.py
|   └── user_maintenance.py
├── schemas/
│   ├── meeting_responce.py  
├── services/
│   ├── ilt_service.py
│   └── ilt_meeting_service.py
└── utils.py
|main.py
|Dockerfile


## Run these two commands docker cmd in root dir/path
# docker build -t middle_ilt_app1 -f DockerFile .
# docker run -p 8000:8000  middle_ilt_app2

## for migration
# alembic revision -m "add crete_by_me column in mdlilts"
# alembic upgrade head