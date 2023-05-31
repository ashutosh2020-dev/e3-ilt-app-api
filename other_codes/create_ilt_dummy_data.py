import requests
import pandas as pd
import random

def hit_create_ilt_api(host_url, ilt, payload={}, header={}):
  endpoint = "api/v1/ilts/"
  url = host_url + endpoint
  params = {"user_id":1, "created_by":1,"title":ilt["title"], "description":ilt["description"], 
                "school_id":1, "member_id": random.sample(range(1, 93), 10)}
  response = requests.post(url, params=params, headers=headers, data=payload)
  print(response.text)

host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
payload = {}
headers = {}
csv_file = pd.read_csv("ilt.csv")
for _,row in csv_file.iterrows():
    try:
        hit_create_ilt_api(host_url=host_url, ilt = row)
    except Exception as e:
        print(f"error{e}")
        pass
print("created successfully")    



