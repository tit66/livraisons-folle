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
client_ids = [c[0] for c in clients]

materials = ['Sable 0/4', 'Gravier 6/14', 'Mélange à Béton', 'Terre Végétale criblée', 'Grave Calcaire 0/31.5']
cities = ['Perpignan', 'Saint-Estève', 'Baho', 'Pia', 'Salses-le-Château', 'Elne']
street_types = ['Route', 'Chemin', 'Allée', 'Impasse', 'Avenue']

today = datetime.now().date()
dates = [today, today + timedelta(days=1), today + timedelta(days=2)]

for i in range(10):
    client_id = random.choice(client_ids)
    material = random.choice(materials)
    qty = random.choice([2.5, 5.0, 10.0, 12.0, 15.0])
    date = random.choice(dates)
    city = random.choice(cities)
    street = random.choice(street_types)
    address = f\"{random.randint(1, 250)} {street} du chantier, {city}\"
    
    run_query(
        '''INSERT INTO orders 
           (client_id, service_type, requested_date, status, dropoff_address, material, quantity_tons) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        (client_id, 'livraison', date, 'pending', address, material, qty)
    )

print('10 livraisons de matériaux injectées avec succès !')
"
