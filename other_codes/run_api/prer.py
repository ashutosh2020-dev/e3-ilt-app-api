import requests
import json
# host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/" 
host_url = "http://127.0.0.1/"

def create_root_user():
    url = host_url+"api/v1/other/root_user/"
    payload = json.dumps({
                "fname": "ashutosh",
                "lname": "tiwari",
                "email": "kmfrm2w@kmkm.com",
                "number": "21545451",
                "password": "mdeijrr3r663",
                "is_active": True,
                "role_id": 3
                })
    headers = {
            'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def create_school():
    school_name_list = ["school_A", "school_B", "school_C", "school_D"]
    payload = {}
    headers = {}
    for school_name in school_name_list:
        url = host_url+f"api/v1/others/schools/"
        payload = json.dumps({
            "name": school_name,
            "location": "none",
            "district": "none"
            })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

def create_role():
    role_name_list = ["member", "facilitator", "admin"]
    description = ["this is member", "this is facilitator", "this is admin"]
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
create_school()
create_root_user()