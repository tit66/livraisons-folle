import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@172.18.0.1:5432/postgres")
try:
    with engine.connect() as conn:
        print("--- DRIVERS ---")
        res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'drivers';"))
        for row in res: print(row)
        print("\n--- VEHICLES ---")
        res = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'vehicles';"))
        for row in res: print(row)
except Exception as e:
    print(e)
