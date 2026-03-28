import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update the UI for Order form
old_mat_block = """        with colA:
            marchandise, quantite, type_benne, volume_benne, action_benne = None, None, None, None, None
            if prestation == "Livraison de matériaux":
                marchandise = st.selectbox("Type de marchandise", ["Sable", "Gravier", "Terre végétale", "Mélange béton"])
                quantite = st.number_input("Quantité (Tonnes)", min_value=0.5, step=0.5, value=1.0)"""

new_mat_block = """        with colA:
            marchandise, quantite, type_benne, volume_benne, action_benne = None, None, None, None, None
            if prestation == "Livraison de matériaux":
                conditionnement = st.radio("Conditionnement", ["En vrac", "En Big Bag"], horizontal=True)
                marchandise = st.selectbox("Type de marchandise", ["Sable", "Gravier", "Terre végétale", "Mélange béton"])
                if conditionnement == "En vrac":
                    quantite = st.number_input("Quantité (Tonnes)", min_value=0.5, step=0.5, value=1.0)
                    volume_benne = None
                else:
                    quantite = st.number_input("Nombre de Big Bags", min_value=1.0, step=1.0, value=1.0)
                    volume_benne = "Big Bag"
"""

if old_mat_block in content:
    content = content.replace(old_mat_block, new_mat_block)
    print("Materials block updated.")
else:
    print("Could not find the materials block.")

# 2. Update the Dashboard display query
old_dash_query = """        SELECT c.name as "Client", o.status as "Statut", 
            o.service_type as "Prestation", COALESCE(o.material, o.waste_type) as "Détails", 
            COALESCE(o.quantity_tons::text || ' T', o.container_type) as "Vol/Poids", 
            o.requested_date as "Date", COALESCE(o.requested_slot, 'Non spécifié') as "Créneau"
        FROM orders o LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d"""

new_dash_query = """        SELECT c.name as "Client", o.status as "Statut", 
            o.service_type as "Prestation", COALESCE(o.material, o.waste_type) as "Détails", 
            CASE 
                WHEN o.container_type = 'Big Bag' THEN o.quantity_tons::int::text || ' x Big Bag'
                ELSE COALESCE(o.quantity_tons::text || ' T', o.container_type) 
            END as "Vol/Poids", 
            o.requested_date as "Date", COALESCE(o.requested_slot, 'Non spécifié') as "Créneau"
        FROM orders o LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d"""

if old_dash_query in content:
    content = content.replace(old_dash_query, new_dash_query)
    print("Dashboard query updated.")
else:
    print("Could not find dashboard query.")

# 3. Update the Mobile mission details formatting
# Find: SELECT o.id, c.name, o.dropoff_address, o.service_type, o.material, o.quantity_tons, o.instructions, o.status FROM orders o
old_mob_query = "SELECT o.id, c.name, o.dropoff_address, o.service_type, o.material, o.quantity_tons, o.instructions, o.status FROM orders o LEFT JOIN clients c ON o.client_id = c.id"
new_mob_query = "SELECT o.id, c.name, o.dropoff_address, o.service_type, o.material, o.quantity_tons, o.container_type, o.instructions, o.status FROM orders o LEFT JOIN clients c ON o.client_id = c.id"

content = content.replace(old_mob_query, new_mob_query)

old_mob_details = """st.write(f"**Détails :** {m['quantity_tons'] if pd.notna(m['quantity_tons']) else '?'} T de {m['material'] if pd.notna(m['material']) else 'Non spécifié'}")"""
new_mob_details = """
                        if pd.notna(m['container_type']) and m['container_type'] == 'Big Bag':
                            st.write(f"**Détails :** {int(m['quantity_tons']) if pd.notna(m['quantity_tons']) else '?'} x Big Bag de {m['material'] if pd.notna(m['material']) else 'Non spécifié'}")
                        else:
                            st.write(f"**Détails :** {m['quantity_tons'] if pd.notna(m['quantity_tons']) else '?'} T de {m['material'] if pd.notna(m['material']) else 'Non spécifié'}")
"""

if old_mob_details in content:
    content = content.replace(old_mob_details, new_mob_details)
    print("Mobile details updated.")
else:
    print("Could not find mobile details display.")

with open("app.py", "w") as f:
    f.write(content)

