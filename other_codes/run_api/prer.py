import requests
import json
import pandas as pd

# host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/" 
host_url = "http://127.0.0.1/"

def create_root_user():
    url = host_url+"api/v1/other/root_user/"
    payload = json.dumps(  {
                "firstName": "ashutosh",
                "lastName": "tiwari",
                "emailId": "as@gmail.com",
                "password": "123456",
                "active": True,
                "roleId": 4
                })
  
    headers = {
            'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def create_distict():
    district = ['Colonial', 'Decatur', 'Gainesville', 'Marion', 'Rio Grande', 'Roanoke', 'Pike', 'York']
    for i in district:
        url = host_url+"api/v1/others/district/"
        payload = json.dumps({
                "name":i
                })
        headers = {
                'Content-Type': 'application/json'
            }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

def create_school():
    d = 1
    district = ['Colonial', 'Decatur', 'Gainesville', 'Marion', 'Rio Grande', 'Roanoke', 'Pike', 'York']
    # school_name_list = ["school_A", "school_B", "school_C", "school_D"]
    school_name_df = pd.read_csv("temp_dis.csv")
    school_name_df = school_name_df.T

    payload = {}
    headers = {}
    print(len(school_name_df.T.columns))
    for j in range(8):

        for school_name in school_name_df.iloc[j]:
            if str(school_name) !="nan":
                url = host_url+f"api/v1/others/schools/"
                payload = json.dumps({
                    "name": school_name,
                    "location": "none",
                    "districtId": j+1
                    })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)

def create_role():
    role_name_list = ["ILT Member", "ILT Facilitator", "Project Leader", "Director"]
    description = ["this is member", "this is facilitator", "this is admin", "this is director"]
    for i in range(len(role_name_list)):
        url = host_url+f"api/v1/others/roles/"
        payload = json.dumps({
                    "role_name": role_name_list[i],
                    "roleDescription": description[i]
                    })
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

create_role()
create_distict()
create_school()
create_root_user()