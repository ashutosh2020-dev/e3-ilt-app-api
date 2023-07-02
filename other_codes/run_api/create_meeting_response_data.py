import requests
import pandas as pd
import json
import random
from datetime import datetime

"""
    create_rock_data()   ->  "meetingResponseId, user_id, name, description, on_track_flag"
    create_to_do_list()  ->  "user_id, meeting_response_id, description, due_date, status"
    create_issues_data() ->  "user_id, meeting_response_id, issue, priority, resolves_flag,
                        recognize_performance_flag, teacher_support_flag, leader_support_flag, 
                        advance_equality_flag, others_flag"
    create_update_data() ->  "user_id, meeting_response_id, description"
"""
num_meetingResponse = 216

def hit_create_rockData_api(host_url, csv_data, meeting_response_id, payload={}, headers={}):
    endpoint = f"api/v1/ilts/meetingResponses/{meeting_response_id}/create_rocks"
    params = {
        "user_id": csv_data["user_id"],
        "name": csv_data["name"],
        "description": csv_data["description"],
        "onTrack": csv_data["on_track_flag"]
    }
    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)

def hit_create_toDoList_api(host_url, csv_data, meeting_response_id, payload={}, headers={}):
    endpoint = f"api/v1/ilts/meetingResponses/{meeting_response_id}/todolist"
    params = {
        "user_id": csv_data['user_id'],
        "meetingResposnceId": meeting_response_id,
        "description": csv_data['description'],
        "status": csv_data['status']
    }
    payload = json.dumps({
        "Duedate": f"{csv_data['due_date']}T00:00:00.000Z"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)

def hit_create_issueData_api(host_url, csv_data,meeting_response_id ,payload={}, headers={}):
    endpoint = f"api/v1/ilts/meetingResponses/{meeting_response_id}/issues"
    params = {
        "user_id": csv_data['user_id'],
        "issue": csv_data['issue'],
        "priority": csv_data['priority'],
        "resolves_flag": csv_data['resolves_flag'],
        "recognize_performance_flag": csv_data['recognize_performance_flag'],
        "teacher_support_flag": csv_data['teacher_support_flag'],
        "leader_support_flag": csv_data['leader_support_flag'],
        "advance_equality_flag": csv_data['advance_equality_flag'],
        "others_flag": csv_data['others_flag']
    }    
    # need to do dynamic
    current_time = datetime.utcnow().isoformat() + "Z"
    payload = json.dumps({
            "CreateAt": current_time
            })
    # payload = json.dumps("2023-06-05T10:39:06.018Z")
    headers = {
    'Content-Type': 'application/json'
    }

    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)

def hit_create_updateData_api(host_url, csv_data,meeting_response_id, payload={}, headers={}):
    endpoint = f"api/v1/ilts/meetingResponses/{meeting_response_id}/updates"
    params = {
        "user_id": csv_data['user_id'],
        "description": csv_data['description']
    }
    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
    print(response.text)
    if '200' not in response.text:
       print(response.text)

def main():
    host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
    # host_url = "http://127.0.0.1/"
    issue_csv = pd.read_csv("issues_data.csv")
    rock_csv = pd.read_csv("rock_data.csv")
    todo_csv = pd.read_csv("todo_list_data.csv")
    update_csv = pd.read_csv("update_data.csv")
    meeting_response_id = [i for i in range(1,num_meetingResponse)]*2
    random.shuffle(meeting_response_id)
    print(len(meeting_response_id))
    for i in range(1, len(meeting_response_id)+1):
        hit_create_rockData_api(host_url, meeting_response_id = meeting_response_id[i], csv_data= rock_csv.iloc[i])
        hit_create_toDoList_api(host_url, meeting_response_id = meeting_response_id[i],  csv_data= todo_csv.iloc[i])
        hit_create_issueData_api(host_url, meeting_response_id = meeting_response_id[i], csv_data= issue_csv.iloc[i])
        hit_create_updateData_api(host_url, meeting_response_id = meeting_response_id[i], csv_data= update_csv.iloc[i])


    print("data created successfully")

main()