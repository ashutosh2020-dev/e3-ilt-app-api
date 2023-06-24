import pandas as pd
from faker import Faker
import random

"""
    create_user_list()
    create_ilt_data()
    crete_ilt_meeting()
"""
user_per_ilt = 7
num_school = 4
num_ilt = 4
num_facilitator = 20
meetings_per_ilt = 2

total_num_user = num_school*num_ilt*user_per_ilt # 112
total_ilts = num_school*num_ilt # 16
total_meetings = total_ilts*meetings_per_ilt # 32

def create_user_list():
    n = total_num_user
    fake = Faker() # Initialize Faker generator
    gmail =[]
    data = []

    for i in range(1, n+1):
        if i <=20:
            role_id = 2
        else:
            role_id = 1
        row = {
            "id":i,
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "email": fake.email(),
            "number": fake.phone_number(),
            "password": fake.password(),
            "is_active": fake.pybool(),
            "role_id": role_id, #random.sample(range(1, 3), 1)[0]
            "parent_id":  random.sample(range(1, num_facilitator), 1)[0] if i >20 else 1 #i-1 if i != 0 else 1 
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
    n = total_ilts
    fake = Faker()
    data = []
    for idx in range(1,n+1):
        member_ids = random.sample(range(1, total_num_user), 6)  # Select 6 random IDs from 1 to 100
        row = {
            "title": fake.job(),
            "description": fake.sentence(),
            "school_id": random.sample(range(1, num_school), 1)[0],
            "owner_id": idx,
            "member_id_list": member_ids,
        }
        data.append(row)

    df = pd.DataFrame(data)
    filename = "ilt.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

def crete_ilt_meeting():
    n = total_meetings #32
    fake = Faker()
    data = []
    for _ in range(n):
        date = fake.date_between(start_date="-30d", end_date="+90d").strftime('%Y-%m-%d')
        row = {
            "ilt_id": random.sample(range(1, total_ilts), 1)[0],
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