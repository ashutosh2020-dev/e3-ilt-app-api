import pandas as pd
from sqlalchemy import create_engine, text

fromdb = "UAT"  # "PROD"
todb = "sqllite"
instance = "dbiltappuat"
DATABASE_URLS_DICT = {
    "PROD": "mysql://sortinghatadmin:Sortinghat#Middle123@rds-middle-ilt-app.c61momvubcsz.us-east-1.rds.amazonaws.com:3306/dbiltapp",
    "UAT": "mysql://sortinghatadmin:Sortinghat#Middle123@rds-middle-ilt-app.c61momvubcsz.us-east-1.rds.amazonaws.com:3306/dbiltappuat",
    "sqllite": "sqlite:///ilt_db.db"
}


def save_db_info(fromdb, todb, instanceName):    
    DATABASE_URL = DATABASE_URLS_DICT.get(fromdb)
    DATABASE_URL2 = DATABASE_URLS_DICT.get(todb)

    conn = create_engine(DATABASE_URL).connect()
    conn2 = create_engine(DATABASE_URL2).connect()
    db_schema = pd.read_sql('SELECT * FROM INFORMATION_SCHEMA.COLUMNS;', conn)


    list_of_table_name = db_schema[db_schema["TABLE_SCHEMA"]== instanceName]["TABLE_NAME"].unique()
    for tname in list_of_table_name:
        df = pd.read_sql_table(tname, conn)
        df.to_sql(tname, conn2, if_exists='replace')
    print("have successfully exported!")
 
save_db_info(fromdb =fromdb , todb = todb, instanceName = instance)