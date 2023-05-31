import pandas as pd
from faker import Faker
import random
# Set the number of rows
n = 10  # Specify the number of rows you want

# Initialize Faker generator
fake = Faker()

# Generate data for each row
data = []
for _ in range(n):
    date = fake.date_between(start_date="+30d", end_date="+90d").strftime('%Y-%m-%d')
    row = {
        "ilt_id": random.sample(range(1, 10), 1)[0],
        "location": fake.city(),
        "startDate": date,
        "meetingStart": fake.time(),
        "meetingEnd": fake.time(),
    }
    data.append(row)

# Create a DataFrame from the data
df = pd.DataFrame(data)

filename = "ilt_meeting.csv"
df.to_csv(filename, index=False)

print(f"Data saved to {filename} successfully!")
