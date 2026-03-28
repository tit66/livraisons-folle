import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add dropoff_address to query_pending and update the checkbox label
old_query = """    query_pending = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.material, o.waste_type) as details, 
               COALESCE(o.quantity_tons::text || ' T', o.container_type) as qty, o.requested_slot, o.status
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d AND o.status IN ('pending', 'assigned')
        ORDER BY o.requested_slot ASC
    \"\"\""""

new_query = """    query_pending = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.material, o.waste_type) as details, 
               COALESCE(o.quantity_tons::text || ' T', o.container_type) as qty, o.requested_slot, o.status, COALESCE(o.dropoff_address, 'Adresse inconnue') as address
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d AND o.status IN ('pending', 'assigned')
        ORDER BY o.requested_slot ASC
    \"\"\""""

if old_query in content:
    content = content.replace(old_query, new_query)
    print("Query pending updated.")

old_label = 'label = f"📦 **N° {row[\'id\']} - {row[\'client_name\']}** | {row[\'service_type\']} | {row[\'qty\']} ({row[\'details\']}) | 🕒 {row[\'requested_slot\']}"'
new_label = 'label = f"📍 {row[\'address\']} | 📦 **{row[\'client_name\']}** | {row[\'service_type\']} | {row[\'qty\']} ({row[\'details\']}) | 🕒 {row[\'requested_slot\']}"'

if old_label in content:
    content = content.replace(old_label, new_label)
    print("Label updated.")

# Fix 2: Update AI table to show address
old_ai_query = 'df_single_o = load_data("SELECT o.id, c.name, o.service_type FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id = :oid", {"oid": o_id})'
new_ai_query = 'df_single_o = load_data("SELECT o.id, c.name, o.service_type, o.dropoff_address FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id = :oid", {"oid": o_id})'

if old_ai_query in content:
    content = content.replace(old_ai_query, new_ai_query)
    
old_ai_row = """                        preview_data.append({
                            "Client (Commande)": f"{client_name} - {service_type}",
                            "👨‍✈️ Chauffeur": dict_d.get(a.get("driver_id"), "Non assigné"),
                            "🚚 Camion": dict_v.get(a.get("vehicle_id"), "Non assigné")
                        })"""

new_ai_row = """                        address = df_single_o.iloc[0]['dropoff_address'] if not df_single_o.empty and pd.notna(df_single_o.iloc[0]['dropoff_address']) else "Inconnue"
                        preview_data.append({
                            "Client & Mission": f"{client_name} - {service_type}",
                            "📍 Lieu": address,
                            "👨‍✈️ Chauffeur": dict_d.get(a.get("driver_id"), "Non assigné"),
                            "🚚 Camion": dict_v.get(a.get("vehicle_id"), "Non assigné")
                        })"""

if old_ai_row in content:
    content = content.replace(old_ai_row, new_ai_row)
    print("AI table updated.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

