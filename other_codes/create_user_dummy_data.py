import requests
import pandas as pd

def hit_create_user_api(host_url, user, payload={}, header={}):
  endpoint = f"""api/v1/users/?fname={user['fname']}&lname={user['lname']}&email={user['email']}&number={user['number']}&password={user['password']}&is_active={user['is_active']}&role_id={1}&UserId={1}"""
  url = host_url + endpoint
  response = requests.post(url, headers=headers, data=payload)
  # print(response.text)

host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
payload = {}
headers = {}
csv_file = pd.read_csv("user.csv")
# print(csv_file)
for _,row in csv_file.iterrows():
    try:
      # print(row)
      hit_create_user_api(host_url=host_url, user = row)
    except Exception as e:
       print(f"error{e}")
       pass
    
print("created successfully")    



