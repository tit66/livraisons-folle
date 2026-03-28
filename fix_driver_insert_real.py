import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure the table schema update is present
if 'ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(50) DEFAULT \'Français\'' not in content:
    init_target = 'safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")'
    if init_target in content:
        content = content.replace(init_target, init_target + '\n    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(50) DEFAULT \'Français\'")')

# Inject nationality in the insert query
old_insert = """                    run_query(\"\"\"
                        INSERT INTO drivers (first_name, last_name, phone, email, license_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry, caces_expiry, is_active, notes)
                        VALUES (:f, :l, :p, :e, :le, :fimo, :dcn, :dce, :cac, true, :notes)
                    \"\"\", {
                        "f": f_name, "l": l_name, "p": phone, "e": email, 
                        "le": date_permis, "fimo": date_fco, "dcn": num_carte, "dce": date_carte, "cac": date_caces, "notes": notes
                    })"""

new_insert = """                    run_query(\"\"\"
                        INSERT INTO drivers (first_name, last_name, nationality, phone, email, license_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry, caces_expiry, is_active, notes)
                        VALUES (:f, :l, :nat, :p, :e, :le, :fimo, :dcn, :dce, :cac, true, :notes)
                    \"\"\", {
                        "f": f_name, "l": l_name, "nat": nat, "p": phone, "e": email, 
                        "le": date_permis, "fimo": date_fco, "dcn": num_carte, "dce": date_carte, "cac": date_caces, "notes": notes
                    })"""

if old_insert in content:
    content = content.replace(old_insert, new_insert)
    print("Insert query updated.")

# Update the display table query (I tried earlier but couldn't find the exact target)
# Let's search for "SELECT id, is_active, first_name, last_name, phone"
table_q_match = re.search(r'load_data\("SELECT id, is_active, first_name, last_name, phone.*?"\)', content)
if table_q_match:
    old_tq = table_q_match.group(0)
    new_tq = old_tq.replace('first_name, last_name, phone', 'first_name, last_name, nationality as langue, phone')
    content = content.replace(old_tq, new_tq)
    print("Table query updated.")

# Also add the dropdown to the form if it's not there
form_target = '                f_name = st.text_input("Prénom *")'
form_new = '                f_name = st.text_input("Prénom *")\n                nat = st.selectbox("Langue / Nationalité", ["Français", "Portugais", "Russe", "Espagnol", "Autre"])'
if form_target in content and 'nat = st.selectbox' not in content:
    content = content.replace(form_target, form_new)
    print("Selectbox added.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
