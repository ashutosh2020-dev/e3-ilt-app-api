import pandas as pd
from faker import Faker
import random

def create_user_list():
    n = 101
    fake = Faker() #Initialize Faker generator
    gmail =[]
    data = []

    for i in range(n):  
        row = {
            "id":i,
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "email": fake.email(),
            "number": fake.phone_number(),
            "password": fake.password(),
            "is_active": fake.pybool(),
            "role_id": random.sample(range(1, 3), 1)[0]
        }
        gmail.append(row["email"])
        data.append(row)
    print(len(gmail))
    print(len(set(gmail)))
    df = pd.DataFrame(data)
    filename = "user.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} successfully!")