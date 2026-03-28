import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add checkbox in UI
target_checkbox = "instructions = st.text_area(\"Instructions spéciales pour le chauffeur\")"
if target_checkbox in content:
    new_checkbox = """instructions = st.text_area("Instructions spéciales pour le chauffeur")
            
        st.divider()
        st.write("### 💶 Facturation & Devis")
        souhaite_devis = st.checkbox("📝 Le client souhaite recevoir un devis avant validation de la prestation")
        if souhaite_devis:
            st.warning("⚠️ Cette commande passera en statut 'Attente de devis' et ne sera pas visible dans le planning tant qu'elle ne sera pas validée.")"""
    content = content.replace(target_checkbox, new_checkbox)
    print("Checkbox UI added.")

# 2. Add variable to INSERT logic
target_insert = """            est_valide = True
            message_erreur = ""
            try:"""
# Let's find where the INSERT INTO orders is done.
target_insert_query = """                        res_o = run_query(\"\"\"
                            INSERT INTO orders (client_id, site_id, status, source, service_type, material, quantity_tons, container_type, waste_type, requested_date, requested_slot, caution_required, requires_return, dropoff_address, instructions)
                            VALUES (:cid, :sid, 'pending', 'internal', :stype, :mat, :qty, :ctype, :wtype, :rdate, :rslot, :caut, :ret, :addr, :inst)
                            RETURNING id
                        \"\"\", {"""

new_insert_query = """                        status_initial = 'attente_devis' if souhaite_devis else 'pending'
                        res_o = run_query(\"\"\"
                            INSERT INTO orders (client_id, site_id, status, source, service_type, material, quantity_tons, container_type, waste_type, requested_date, requested_slot, caution_required, requires_return, dropoff_address, instructions)
                            VALUES (:cid, :sid, :stat, 'internal', :stype, :mat, :qty, :ctype, :wtype, :rdate, :rslot, :caut, :ret, :addr, :inst)
                            RETURNING id
                        \"\"\", {\"stat\": status_initial, """

if target_insert_query in content:
    content = content.replace(target_insert_query, new_insert_query)
    print("Insert logic updated.")
else:
    print("Insert logic not found. Trying regex.")
    match = re.search(r'INSERT INTO orders.*?\'pending\'', content, re.DOTALL)
    if match:
        content = content.replace("'pending'", ":stat")
        # Then we need to add the parameter mapping... this is getting complex via regex.
        # Let's write a python script to patch the query dynamically.

