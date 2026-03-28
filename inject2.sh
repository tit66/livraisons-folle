docker exec livraisons-app_streamlit_1 python -c "
import psycopg2
from datetime import datetime, timedelta
import random

def get_conn():
    return psycopg2.connect('postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n')

def run_query(query, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            conn.commit()

clients = run_query('SELECT id FROM clients LIMIT 5')
if not clients:
    run_query('INSERT INTO clients (name, type, email) VALUES (%s, %s, %s)', ('Client Test 1', 'pro', 'test1@test.com'))
    run_query('INSERT INTO clients (name, type, email) VALUES (%s, %s, %s)', ('Client Test 2', 'particulier', 'test2@test.com'))
    clients = run_query('SELECT id FROM clients LIMIT 5')

client_ids = [c[0] for c in clients]

today = datetime.now().date()
tomorrow = today + timedelta(days=1)
sunday = today + timedelta(days=2)

dates = [today, tomorrow, sunday]
services = ['pose', 'retrait', 'rotation']

for date in dates:
    for i in range(3):
        client_id = random.choice(client_ids)
        service = random.choice(services)
        
        run_query(
            '''INSERT INTO orders 
               (client_id, service_type, scheduled_date, status, address, city, skip_size) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (client_id, service, date, 'pending', f'Rue Test {i} ({date})', 'Perpignan', '8m3')
        )
        print(f'Injected {service} for {date}')
"
