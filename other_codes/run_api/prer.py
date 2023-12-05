import requests
import json
import pandas as pd

# host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/" 
host_url = "http://127.0.0.1/"

def create_root_user():
    
    url = host_url+"api/v1/other/root_user/"
    
    csv_file = pd.read_excel(
        r"C:\ashutosh_tiwari\sortingHat\middle-ilt-app-api\other_codes\run_api\director_cred.xlsx")
    for _, user in csv_file.iterrows():
        payload = json.dumps(  {
                    "firstName": user["firstName"],
                    "lastName": user["lastName"],
                    "emailId": user["emailId"],
                    "password": user["password"],
                    "active": user["active"],
                    "roleId": user["roleId"]
                    })
    
        headers = {
                'Content-Type': 'application/json'
            }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
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
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)

def create_school():
    d = 1
    district = ['Colonial', 'Decatur', 'Gainesville', 'Marion', 'Rio Grande', 'Roanoke', 'Pike', 'York']
    # school_name_list = ["school_A", "school_B", "school_C", "school_D"]
    school_name_df = pd.read_csv(r"C:\ashutosh_tiwari\sortingHat\middle-ilt-app-api\other_codes\run_api\temp_dis.csv")
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
                response = requests.request("POST", url, headers=headers, data=payload, verify=False)
                print(response.text)

def create_role():
    role_name_list = ["ILT Member", "ILT Facilitator", "Project Leader", "Director"]
    description = ["this is member", "this is facilitator", "this is admin", "this is director"]
    for i in range(len(role_name_list)):
        url =  host_url+f"api/v1/others/roles/"
        payload = json.dumps({
                    "role_name": role_name_list[i],
                    "roleDescription": description[i]
                    })
        headers = { 
                     'accept': 'application/json',
                    'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)


def create_priority():
    name_list = ["High", "Medium", "Low", "No Longer Needed"]
    description = ["High priority", "Medium priority", "Low priority", "No Longer Needed"]
    for i in range(len(name_list)):
        url = host_url+f"api/v1/others/priority/"
        payload = json.dumps({
                    "name": name_list[i],
                    "description": description[i]
                    })
        headers = { 
                     'accept': 'application/json',
                    'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(response.text)

create_role()
create_distict()
create_school()
create_priority()
create_root_user()
