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
    member_ids = random.sample(range(1, 95), 10)  # Select 10 random IDs from 1 to 100
    row = {
        "title": fake.job(),
        "description": fake.sentence(),
        "school_id": fake.random_number(digits=4),
        "member_id_list": member_ids,
    }
    data.append(row)

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Save DataFrame to a CSV file
filename = "ilt.csv"
df.to_csv(filename, index=False)

print(f"Data saved to {filename} successfully!")
