# middle-ILT-app-api-code

# structure
app/
├── config/
│   ├── app_settings.py
│   └── database.py
├── models.py
├── routers/
│   ├── users.py
│   └── orders.py
├── services/
│   ├── user_service.py
│   └── order_service.py
└── utils.py

# extra
# try:
#     users = db.query(User).limit(5).all()
#     for user in users:
#         print(user.id, user.user_id,user.password)
# except Exception as e:
#     print("Error retrieving data from the database:", e)
# finally:
#     db.close()