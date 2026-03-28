import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update init_connection to add column safely
init_target = 'safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")'
if init_target in content:
    init_new = init_target + '\n    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(50) DEFAULT \'Français\'")'
    content = content.replace(init_target, init_new)

# 2. Add input to form
form_target = '                f_name = st.text_input("Prénom *")'
if form_target in content:
    form_new = '                f_name = st.text_input("Prénom *")\n                nat = st.selectbox("Langue / Nationalité", ["Français", "Portugais", "Russe", "Espagnol", "Autre"])'
    content = content.replace(form_target, form_new)

# 3. Update insert logic
insert_target_if = '                if f_name and l_name:'
if insert_target_if in content:
    # We need to find the insert query.
    match = re.search(r'run_query\("INSERT INTO drivers \(first_name, last_name, phone, email, license_number, license_types, license_expiry, caces, caces_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry\) VALUES \(:fn, :ln, :ph, :em, :lnum, :lty, :lexp, :cac, :cexp, :fco, :dcnum, :dcexp\)", {.*?}\)', content, re.DOTALL)
    if match:
        old_insert = match.group(0)
        new_insert = old_insert.replace(
            'driver_card_expiry)',
            'driver_card_expiry, nationality)'
        ).replace(
            ':dcexp)", {',
            ':dcexp, :nat)", { "nat": nat, '
        )
        content = content.replace(old_insert, new_insert)
        print("Insert logic updated.")
    else:
        print("Insert logic NOT FOUND. Using fallback.")
        # Attempt fallback replacement based on likely structure if exact match fails
        match_fallback = re.search(r'run_query\("INSERT INTO drivers.*?VALUES \(:fn, :ln.*?\)", {.*?}\)', content, re.DOTALL)
        if match_fallback:
            old_ins = match_fallback.group(0)
            new_ins = old_ins.replace(
                'driver_card_expiry)',
                'driver_card_expiry, nationality)'
            ).replace(
                ':dcexp)", {',
                ':dcexp, :nat)", {\n                        "nat": nat,'
            )
            content = content.replace(old_ins, new_ins)
            print("Fallback insert logic updated.")

# 4. Update the display table query
query_target = 'df_drivers = load_data("SELECT id, is_active, first_name, last_name, phone, license_types as permis, license_expiry as fin_permis, fimo_fco_expiry as fin_fco, driver_card_expiry as fin_carte, caces, caces_expiry as fin_caces FROM drivers ORDER BY first_name")'
if query_target in content:
    query_new = 'df_drivers = load_data("SELECT id, is_active, first_name, last_name, nationality as langue, phone, license_types as permis, license_expiry as fin_permis, fimo_fco_expiry as fin_fco, driver_card_expiry as fin_carte, caces, caces_expiry as fin_caces FROM drivers ORDER BY first_name")'
    content = content.replace(query_target, query_new)
    print("Table view updated.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Nationality field injected.")
