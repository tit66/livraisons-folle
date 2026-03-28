docker exec livraisons-app_streamlit_1 python -c "
import psycopg2
from datetime import datetime, timedelta
import random

def run_query(query, params=None):
    with psycopg2.connect('postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n') as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            conn.commit()

clients = run_query('SELECT id, name FROM clients')
if not clients:
    run_query('INSERT INTO clients (name, type, email) VALUES (%s, %s, %s)', ('Client Auto 1', 'pro', 'auto1@test.com'))
    clients = run_query('SELECT id, name FROM clients')

client_ids = [c[0] for c in clients]

service_types = ['pose', 'retrait', 'rotation']
waste_types = ['DIB', 'Gravats', 'Bois', 'Carton', 'Ferraille']
cities = ['Perpignan', 'Canet-en-Roussillon', 'Cabestany', 'Rivesaltes', 'Toulouges', 'Bompas', 'Le Soler']
street_types = ['Rue', 'Avenue', 'Boulevard', 'Impasse', 'Chemin']

today = datetime.now().date()
dates = [today, today + timedelta(days=1), today + timedelta(days=2)]

for i in range(20):
    client_id = random.choice(client_ids)
    service = random.choice(service_types)
    waste = random.choice(waste_types)
    date = random.choice(dates)
    city = random.choice(cities)
    street = random.choice(street_types)
    address = f\"{random.randint(1, 150)} {street} des Oliviers, {city}\"
    
    run_query(
        '''INSERT INTO orders 
           (client_id, service_type, requested_date, status, dropoff_address, waste_type) 
           VALUES (%s, %s, %s, %s, %s, %s)''',
        (client_id, service, date, 'pending', address, waste)
    )

print('20 commandes injectées avec succès !')
"
