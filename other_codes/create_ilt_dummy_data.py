import requests
import pandas as pd
import random


num_school = 4
num_ilt = 4
# owner_ids = list(df[df['role_id']==2].index)
owner_ids=[3, 4, 5, 6, 8, 11, 12, 14, 15, 18, 20, 24, 26, 28, 31, 32, 33, 34, 35, 
            36, 37, 38, 45, 47, 53, 58, 60, 61, 63, 64, 65, 66, 70, 71, 74, 75, 77, 
            78, 87, 89, 94, 96, 97, 99, 100, 102, 103, 108]

def hit_create_ilt_api(host_url, ilt, owner_id, school_id):
        endpoint = "api/v1/ilts/"
        url = host_url + endpoint
        members = random.sample(range(1, 112), 6) 
        members.append(owner_id)
        unique_members = list(set(members))  
        params = {"user_id":1, 
                  "Ilt_owner_id":owner_id,
                  "title":ilt["title"], 
                  "description":ilt["description"], 
                  "school_id":school_id, 
                  "member_id": unique_members
                  }
        payload = {}
        headers = {}
        response = requests.post(url, params=params, headers=headers, data=payload)
        print(response.text)



host_url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/"
# host_url = "http://127.0.0.1/"
csv_file = pd.read_csv("ilt.csv")
for school_idx in range(num_school):
  for i,row in csv_file.iterrows():
      if i==num_ilt:
          break
      try:
          hit_create_ilt_api(host_url=host_url, ilt=row, owner_id = owner_ids[i+(school_idx*num_ilt)], school_id=(school_idx+1))
      except Exception as e:
          print(f"error{e}")
          pass
print("created successfully")