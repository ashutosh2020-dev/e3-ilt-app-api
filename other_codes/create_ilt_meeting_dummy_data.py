import requests
import pandas as pd
import random
import json

def hit_create_iltMeeting_api(host_url, ilt_meeting):
    date = ilt_meeting['startDate']
    print(date)
    params = {"user_id":1, "ilt_id":ilt_meeting["ilt_id"],"location":ilt_meeting["location"]}
    payload = json.dumps({
    "scheduledStartDate": f"{date}T{ilt_meeting['meetingStart']}.345Z",
    "meetingStart": f"{date}T{ilt_meeting['meetingStart']}.345Z",
    "meetingEnd": f"{date}T{ilt_meeting['meetingEnd']}.345Z"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    endpoint = "api/v1/ilts/{id}/meetings/"
    url = host_url + endpoint
    response = requests.post(url, params=params, headers=headers, data=payload)
    print(response.text)


host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
csv_file = pd.read_csv("ilt_meeting.csv")
for _,row in csv_file.iterrows():
    try:
        hit_create_iltMeeting_api(host_url=host_url, ilt_meeting = row)
    except Exception as e:
        print(f"error{e}")
        pass
print("created successfully")    



