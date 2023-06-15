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

# owner_ids = list(df[df['role_id']==2].index)
facilitator_ids=[3, 4, 5, 6, 8, 11, 12, 14, 15, 18, 20, 24, 26, 28, 31, 32, 33, 34, 35, 
            36, 37, 38, 45, 47, 53, 58, 60, 61, 63, 64, 65, 66, 70, 71, 74, 75, 77, 
            78, 87, 89, 94, 96, 97, 99, 100, 102, 103, 108]
# host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/" 
host_url = "http://127.0.0.1/"




def hit_create_user_api(host_url, user, payload={}, headers={}):
    endpoint = f"""api/v1/users/?"""
    params = {"fname":user['fname'], 
              "lname":user['lname'],
              "email":user['email'],
              "number":user['number'],
              "password":user['password'],
              "is_active": user['is_active'],
              "role_id":user['role_id'], 
              "UserId":user['parent_id'] }
    
    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
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
        endpoint = "api/v1/ilts/"
        url = host_url + endpoint
        members_ids = []
        while len(members_ids) < num_member_in_ilt:
            new_id = random.randint(2, total_num_user)
            if new_id not in members_ids:
                members_ids.append(new_id)
        if ilt["owner_id"] not in members_ids:
            members_ids[0] = ilt["owner_id"]
          
        params = {"user_id":1, 
                  "Ilt_owner_id":ilt["owner_id"],
                  "title":ilt["title"], 
                  "description":ilt["description"], 
                  "school_id":school_id, 
                  "member_id": members_ids
                  }
        payload = {}
        headers = {}
        response = requests.post(url, params=params, headers=headers, data=payload)
        print(response.text)

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
