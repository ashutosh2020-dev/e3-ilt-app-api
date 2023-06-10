import requests
import pandas as pd

def hit_create_user_api(host_url, user, payload={}, headers={}):
    endpoint = f"""api/v1/users/?"""
    parent_id = user['id']-1 if user['id'] != 0 else 1 
    params = {"fname":user['fname'], 
              "lname":user['lname'],
              "email":user['email'],
              "number":user['number'],
              "password":user['password'],
              "is_active": user['is_active'],
              "role_id":user['role_id'], 
              "UserId":parent_id}
    
    url = host_url + endpoint 
    response = requests.post(url, params=params, headers=headers, data=payload)
    if '200' not in response.text:
       print(response.text)


host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
# host_url = "http://127.0.0.1/"
payload = {}
headers = {}
csv_file = pd.read_csv("user.csv")

for _, row in csv_file.iterrows():
    try:
      hit_create_user_api(host_url=host_url, user = row)
    except Exception as e:
       print(f"error{e}")
       pass
    
print("created successfully")

