import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure the table schema update is present
if 'ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(50) DEFAULT \'Français\'' not in content:
    init_target = 'safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")'
    if init_target in content:
        init_new = init_target + '\n    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS nationality VARCHAR(50) DEFAULT \'Français\'")'
        content = content.replace(init_target, init_new)

# Force inject the nationality variable into the insert query
insert_search = re.search(r'run_query\("INSERT INTO drivers \(first_name, last_name, phone, email, license_number, license_types, license_expiry, caces, caces_expiry, fimo_fco_expiry, driver_card_number, driver_card_expiry\) VALUES \(:fn, :ln, :ph, :em, :lnum, :lty, :lexp, :cac, :cexp, :fco, :dcnum, :dcexp\)", {.*?}\)', content, re.DOTALL)

if insert_search:
    old_code = insert_search.group(0)
    new_code = old_code.replace(
        'driver_card_expiry)',
        'driver_card_expiry, nationality)'
    ).replace(
        ':dcexp)", {',
        ':dcexp, :nat)", {\n                        "nat": nat,'
    )
    content = content.replace(old_code, new_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Driver insert code updated successfully.")
else:
    print("Pattern not found. Using brute force replace.")
    
