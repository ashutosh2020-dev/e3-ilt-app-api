import pandas as pd
from faker import Faker

# Set the number of rows
n = 100  # Specify the number of rows you want


# Initialize Faker generator
fake = Faker()
gmail =[]
# Generate data for each row
data = []
for _ in range(n):
    row = {
        "fname": fake.first_name(),
        "lname": fake.last_name(),
        "email": fake.email(),
        "number": fake.phone_number(),
        "password": fake.password(),
        "is_active": fake.pybool(),
        "role_id": fake.random_number(digits=2)
    }
    gmail.append(row["email"])
    data.append(row)
print(len(gmail))
print(len(set(gmail)))

# Create a DataFrame from the data
df = pd.DataFrame(data)
# Save DataFrame to a CSV file
filename = "user.csv"
df.to_csv(filename, index=False)

print(f"Data saved to {filename} successfully!")
