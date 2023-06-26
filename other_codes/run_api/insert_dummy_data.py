import requests
import pandas as pd
import random
import json
"""
 hit_create_ilt_api()
hit_create_iltMeeting_api()
hit_create_user_api()

run_create_user_api()
run_create_ilt_api()
run_create_iltMeeting_api()
"""
num_user = 112
num_school = 4
num_ilt = 4
num_member_in_ilt = 7
meetings_per_ilt = 2
user_per_ilt = 7
total_num_user = num_school*num_ilt*user_per_ilt # 112
total_ilts = num_school*num_ilt # 16
total_meetings = total_ilts*meetings_per_ilt # 32

host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/" 
# host_url = "http://127.0.0.1/"

def hit_create_user_api(host_url, user, payload={}, headers={}):
    endpoint = f"""api/v1/users/"""
    url = host_url + endpoint 
    payload = json.dumps({
                "firstName": user['fname'],
                "lastName": user['lname'],
                "emailId": user['email'],
                "phoneNumber": user['number'],
                "password": user['password'],
                "active": user['is_active'],
                "roleId": user['role_id']
                })
    headers = {
                'Content-Type': 'application/json',
                'UserId':str(user['parent_id'])
                }
    response = requests.post(url, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)

def run_create_user_api():
    csv_file = pd.read_csv("user.csv")
    for _, row in csv_file.iterrows():
        try:
          hit_create_user_api(host_url=host_url, user = row)
        except Exception as e:
          print(f"error{e}")
          pass
    print("created successfully")

def generate_random_id():
    return random.randint(1, total_num_user)

def hit_create_ilt_api(host_url, ilt, school_id):
        user_id = 10
        ilt["owner_id"] = int(ilt["owner_id"])
        endpoint = f"api/v1/ilts/"
        url = host_url + endpoint
        members_ids = []
        while len(members_ids) < num_member_in_ilt:
            new_id = random.randint(2, total_num_user)
            if new_id not in members_ids:
                members_ids.append(new_id)
        if ilt["owner_id"] not in members_ids:
            members_ids[0] = ilt["owner_id"]

        # Convert members_ids to regular integers
        members_ids = [int(id) for id in members_ids]
        # print(ilt["description"], ilt["title"])
        # print(type(ilt["description"]), type(ilt["title"]), type(ilt["owner_id"]))
        # params = {"user_id": 1}
        payload = json.dumps({  "title": ilt["title"],
                                "description": ilt["description"],
                                "schoolId": school_id,
                                "owner_id": ilt["owner_id"],
                                "memberIds": members_ids
                            })
        headers = {
            'Content-Type': 'application/json',
            'UserId':str(user_id)
        }
        print("================")
        response = requests.post(url, headers=headers, data=payload)
        # response = requests.request("POST", url, headers=headers, json=payload)
        print(response.text)

def hit_create_iltMeeting_api(host_url, ilt_meeting, ilt_owner_id, ilt_id):
    date = ilt_meeting['startDate']
    payload = json.dumps({
                            "scheduledStartDate": f"{date}T{ilt_meeting['meetingStart']}.00",
                            "meetingStart": f"{date}T{ilt_meeting['meetingStart']}.00",
                            "meetingEnd": f"{date}T{ilt_meeting['meetingEnd']}.00", 
                            "location":ilt_meeting["location"]
                        })
    
    headers = {
            'Content-Type': 'application/json',
            "UserId":str(ilt_owner_id)
            }
    endpoint = f"api/v1/ilts/{ilt_id}/meetings/"
    url = host_url + endpoint
    response = requests.post(url, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)

def run_create_ilt_api():
    csv_file = pd.read_csv("ilt.csv")
    for school_idx in range(num_school):
        for i in range(num_ilt):
            if i==num_ilt:
                break
            try:
                hit_create_ilt_api( host_url=host_url,
                                    ilt=csv_file.iloc[i+(school_idx*num_ilt)],  
                                    school_id=(school_idx+1)
                                    )
            except Exception as e:
                print(f"error{e}")
                pass
        
            
    print("created successfully")

def run_create_iltMeeting_api():
    owner_ids = [i for i in range(1,total_ilts+1)]*2 # facilitator ids, no need to calculate
    ilt_ids = [i for i in range(1,total_ilts+1)] *2 # wrt ilt ids   
    

    csv_file = pd.read_csv("ilt_meeting.csv")
    for i in range(total_meetings):
        try:
            hit_create_iltMeeting_api(host_url=host_url, ilt_meeting = csv_file.iloc[i], 
                                      ilt_id = ilt_ids[i], ilt_owner_id = owner_ids[i])
        except Exception as e:
            print(f"error : {e}")
            print("i = ",i, "ilt", ilt_ids[i])
            pass

    print("created successfully")

if __name__ == "__main__":
    run_create_user_api()
    run_create_ilt_api()
    run_create_iltMeeting_api()
