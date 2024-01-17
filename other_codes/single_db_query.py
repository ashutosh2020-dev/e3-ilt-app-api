from sqlalchemy import create_engine, text
import pandas as pd

DATABASE_URL = "mysql://sortinghatadmin:Sortinghat#Middle123@rds-middle-ilt-app.c61momvubcsz.us-east-1.rds.amazonaws.com:3306/dbiltappuat"

# engine = create_engine(DATABASE_URL)
# with engine.connect() as conn:
#     user_cset_record = conn.execute(text(f"SELECT * FROM roles;"))
#     for re in user_cset_record:
#         print(type(re))
#         break
df = pd.read_sql_table('roles', DATABASE_URL)
print(df.shape)