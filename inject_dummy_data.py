import datetime
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://n8n:supersecret@n8n-local_postgres_1:5432/n8n")

with engine.begin() as conn:
    # 1. Création de clients factices avec les bons types
    res = conn.execute(text("INSERT INTO clients (name, type, email, phone, billing_address) VALUES ('Entreprise Dubois BTP', 'pro_compte', 'contact@dubois-btp.fr', '0612345678', '10 rue des Artisans, 66000 Perpignan') RETURNING id")).fetchone()
    client1_id = res[0]
    
    res = conn.execute(text("INSERT INTO clients (name, type, email, phone, billing_address) VALUES ('M. Martin Paul', 'particulier', 'paul.martin@email.com', '0698765432', '5 avenue des Fleurs, 66330 Cabestany') RETURNING id")).fetchone()
    client2_id = res[0]

    # 2. Création de chantiers factices
    res = conn.execute(text("INSERT INTO sites (client_id, label, address, is_active) VALUES (:cid, 'Chantier Centre-Ville', '15 rue de la République, 66000 Perpignan', true) RETURNING id"), {"cid": client1_id}).fetchone()
    site1_id = res[0]
    
    res = conn.execute(text("INSERT INTO sites (client_id, label, address, is_active) VALUES (:cid, 'Maison', '5 avenue des Fleurs, 66330 Cabestany', true) RETURNING id"), {"cid": client2_id}).fetchone()
    site2_id = res[0]

    # 3. Création de commandes pour DEMAIN
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    conn.execute(text("""
        INSERT INTO orders (client_id, site_id, service_type, container_type, waste_type, status, source, requested_date, requested_slot)
        VALUES (:cid, :sid, 'Benne - Pose', '8m3', 'Gravats', 'pending', 'dummy_injection', :req_date, '8h (Premier tour)')
    """), {"cid": client1_id, "sid": site1_id, "req_date": tomorrow})

    conn.execute(text("""
        INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, instructions, status, source, requested_date, requested_slot)
        VALUES (:cid, :sid, 'Livraison de matériaux', 'Sable', 2.0, 'Attention ruelle étroite, reculer en arrivant.', 'pending', 'dummy_injection', :req_date, '13h - 15h')
    """), {"cid": client1_id, "sid": site1_id, "req_date": tomorrow})

    conn.execute(text("""
        INSERT INTO orders (client_id, site_id, service_type, container_type, waste_type, status, source, requested_date, requested_slot)
        VALUES (:cid, :sid, 'Benne - Rotation', '15m3', 'DIB (Tout venant)', 'pending', 'dummy_injection', :req_date, 'Indifférent dans la journée')
    """), {"cid": client2_id, "sid": site2_id, "req_date": tomorrow})

print("Données factices injectées avec succès !")
