import psycopg2
from datetime import datetime, timedelta
import random

def get_conn():
    return psycopg2.connect("postgresql://postgres:postgres@localhost:5432/livraisons")

def run_query(query, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            conn.commit()

# Ensure clients exist
clients = run_query("SELECT id FROM clients LIMIT 5")
if not clients:
    run_query("INSERT INTO clients (name, type, email) VALUES (%s, %s, %s)", ('Client Test 1', 'pro', 'test1@test.com'))
    run_query("INSERT INTO clients (name, type, email) VALUES (%s, %s, %s)", ('Client Test 2', 'particulier', 'test2@test.com'))
    clients = run_query("SELECT id FROM clients LIMIT 5")

client_ids = [c[0] for c in clients]

today = datetime.now().date()
tomorrow = today + timedelta(days=1)
sunday = today + timedelta(days=2)

dates_to_inject = [today, tomorrow, sunday]
service_types = ['pose', 'retrait', 'rotation']

for date in dates_to_inject:
    for i in range(3):
        client_id = random.choice(client_ids)
        service = random.choice(service_types)
        
        run_query(
            """INSERT INTO orders 
               (client_id, service_type, scheduled_date, status, address, city, skip_size) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                client_id,
                service,
                date,
                "pending", # Using pending so they can be assigned in Planning
                f"Rue Test {i}",
                "Perpignan",
                "8m3"
            )
        )
        print(f"Injected {service} order for {date}")

print("Done injecting weekend orders.")
