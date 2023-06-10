import requests
import pandas as pd
import random
import json

num_ilt = 16
host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
# host_url = "http://127.0.0.1/"
owner_ids = [i for i in range(1,num_ilt+1)]*2 # facilitator ids, no need to calculate
ilt_ids = [i for i in range(1,num_ilt+1)] *2 # wrt ilt ids   


def hit_create_iltMeeting_api(host_url, ilt_meeting, ilt_owner_id, ilt_id):
    date = ilt_meeting['startDate']
    params = {
            "user_id":ilt_owner_id, 
            "ilt_id":ilt_id,
            "location":ilt_meeting["location"]
            }
    payload = json.dumps({
                            "scheduledStartDate": f"{date}T{ilt_meeting['meetingStart']}.00",
                            "meetingStart": f"{date}T{ilt_meeting['meetingStart']}.00",
                            "meetingEnd": f"{date}T{ilt_meeting['meetingEnd']}.00"
                        })
    
    headers = {
            'Content-Type': 'application/json'
            }
    endpoint = "api/v1/ilts/{id}/meetings/"
    url = host_url + endpoint
    response = requests.post(url, params=params, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)



csv_file = pd.read_csv("ilt_meeting.csv")
for i, row in csv_file.iterrows():
    try:
        hit_create_iltMeeting_api(host_url=host_url, ilt_meeting = row, ilt_id = ilt_ids[i], ilt_owner_id = owner_ids[row["ilt_id"]])
    except Exception as e:
        print(f"error{e}")
        pass

print("created successfully")