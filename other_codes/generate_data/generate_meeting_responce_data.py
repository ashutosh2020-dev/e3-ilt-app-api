import pandas as pd
from faker import Faker
import random

"""
    create_rock_data()   ->  "meetingResponseId, user_id, name, description, on_track_flag"
    create_to_do_list()  ->  "user_id, meeting_response_id, description, due_date, status"
    create_issues_data() ->  "user_id, meeting_response_id, issue, priority, resolves_flag, recognize_performance_flag, teacher_support_flag, leader_support_flag, advance_equality_flag, others_flag"
    create_update_data() ->  "user_id, meeting_response_id, description"
"""
user_per_ilt = 7
num_school = 4
num_ilt = 4
meetings_per_ilt = 2

total_num_user = num_school*num_ilt*user_per_ilt # 112
total_ilts = num_school*num_ilt # 16
total_meetings = total_ilts*meetings_per_ilt # 32

total_meetingResponse = total_meetings*user_per_ilt #224
num_of_priority = 25
num_of_rock = 25

total_responce_data =total_meetingResponse * 2 # 448

def create_rock_data():
    n = total_responce_data # 448
    fake = Faker()
    data = []
    for _ in range(n):
        row = {
            "meetingResponseId": fake.random_int(min=1, max=total_meetingResponse),
            "user_id": fake.random_int(min=1, max=total_num_user),
            "name": fake.word().capitalize(),
            "description": fake.sentence(),
            "on_track_flag": random.choice([True, False]),
        }
        data.append(row)
    df = pd.DataFrame(data)
    filename = "rock_data.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

def create_to_do_list():
    n = total_responce_data # 448
    fake = Faker()
    data = []
    for _ in range(n):
        row = {
            "user_id": fake.random_int(min=1, max=100),
            "meeting_response_id": fake.random_int(min=1, max=total_meetingResponse),
            "description": fake.sentence(),
            "due_date": fake.date_between(start_date="+1d", end_date="+30d").strftime('%Y-%m-%d'),
            "status": random.choice(["Not Started", "On Going", "Completed"]),
        }
        data.append(row)
    df = pd.DataFrame(data)
    filename = "todo_list_data.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

def create_issues_data():
    n = total_responce_data # 448
    fake = Faker()
    data = []
    for _ in range(n):
        row = {
            "user_id": fake.random_int(min=1, max=100),
            "meeting_response_id": fake.random_int(min=1, max=total_meetingResponse),
            "issue": fake.sentence(),
            "priority": fake.random_int(min=1, max=num_of_priority),
            "resolves_flag": random.choice([True, False]),
            "recognize_performance_flag": random.choice([True, False]),
            "teacher_support_flag": random.choice([True, False]),
            "leader_support_flag": random.choice([True, False]),
            "advance_equality_flag": random.choice([True, False]),
            "others_flag": random.choice(["Top", "Medium", "Low"]),
        }
        data.append(row)
    df = pd.DataFrame(data)
    filename = "issues_data.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")

def create_update_data():
    n = total_responce_data # 448
    fake = Faker()
    data = []
    for _ in range(n):
        row = {
            "user_id": fake.random_int(min=1, max=100),
            "meeting_response_id": fake.random_int(min=1, max=total_meetingResponse),
            "description": fake.sentence(),
        }
        data.append(row)
    df = pd.DataFrame(data)
    filename = "update_data.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")
    


create_rock_data()
create_to_do_list()
create_issues_data()
create_update_data()