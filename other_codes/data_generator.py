import pandas as pd
from faker import Faker
import random

"""
    create_user_list()
    create_ilt_data()
    crete_ilt_meeting()
"""
num_of_user = 112
num_of_ilt = 16
num_of_meetings = 32
def create_user_list():
    n = num_of_user
    fake = Faker() # Initialize Faker generator
    gmail =[]
    data = []

    for i in range(1, n+1):
        row = {
            "id":i,
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "email": fake.email(),
            "number": fake.phone_number(),
            "password": fake.password(),
            "is_active": fake.pybool(),
            "role_id": random.sample(range(1, 3), 1)[0]
        }
        gmail.append(row["email"])
        data.append(row)
    print(len(gmail))
    print(len(set(gmail)))
    df = pd.DataFrame(data)
    filename = "user.csv"
    df.to_csv(filename, index=False)    
    print(f"Data saved to {filename} successfully!")

def create_ilt_data():
    n = num_of_ilt
    fake = Faker()
    data = []
    for _ in range(n):
        member_ids = random.sample(range(1, 112), 6)  # Select 6 random IDs from 1 to 100
        row = {
            "title": fake.job(),
            "description": fake.sentence(),
            "school_id": fake.random_number(digits=1),
            "member_id_list": member_ids,
        }
        data.append(row)

    df = pd.DataFrame(data)
    filename = "ilt.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

def crete_ilt_meeting():
    n = num_of_meetings #32
    fake = Faker()
    data = []
    for _ in range(n):
        date = fake.date_between(start_date="+30d", end_date="+90d").strftime('%Y-%m-%d')
        row = {
            "ilt_id": random.sample(range(1, 16), 1)[0],
            "location": fake.city(),
            "startDate": date,
            "meetingStart": fake.time(),
            "meetingEnd": fake.time(),
        }
        data.append(row)
    df = pd.DataFrame(data)
    filename = "ilt_meeting.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

create_user_list()
create_ilt_data()
crete_ilt_meeting()