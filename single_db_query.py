from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///t.db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    user_cset_record = conn.execute(text(f"SELECT schedule_start_at FROM Ilt_meetings LIMIT 1;"))
    d = [i for i in user_cset_record][0][0]
    print(d)
    # for row in user_cset_record:
    #     print(row)    


    # l1=[]
    # for i in user_cset_record:
    #     l1.append(i[0])
    # print(l1)
    print(" successfully")
