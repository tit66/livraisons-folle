import pandas as pd
from datetime import datetime, timedelta
import random

# Assuming app.py has init_connection and run_query
from app import init_connection, run_query

engine = init_connection()

# Get some clients
clients = pd.read_sql_query("SELECT id FROM clients LIMIT 5", engine)
if clients.empty:
    run_query("INSERT INTO clients (name, type, email) VALUES ('Client Test 1', 'pro', 'test1@test.com')", {})
    run_query("INSERT INTO clients (name, type, email) VALUES ('Client Test 2', 'particulier', 'test2@test.com')", {})
    clients = pd.read_sql_query("SELECT id FROM clients LIMIT 5", engine)

client_ids = clients['id'].tolist()

today = datetime.now().date()
tomorrow = today + timedelta(days=1)
sunday = today + timedelta(days=2) # Assuming today is Friday

dates_to_inject = [today, tomorrow, sunday]
service_types = ['pose', 'retrait', 'rotation']
status = 'planned'

for date in dates_to_inject:
    for i in range(3):
        client_id = random.choice(client_ids)
        service = random.choice(service_types)
        
        run_query(
            """INSERT INTO orders 
               (client_id, service_type, scheduled_date, status, address, city, skip_size) 
               VALUES (:cid, :srv, :sdate, :st, :addr, :city, :size)""",
            {
                "cid": client_id,
                "srv": service,
                "sdate": date,
                "st": "pending",
                "addr": f"Rue Test {i}",
                "city": "Perpignan",
                "size": "8m3"
            }
        )
        print(f"Injected {service} order for {date}")

print("Done injecting weekend orders.")
