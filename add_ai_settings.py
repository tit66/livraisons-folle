import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ensure system_settings table exists
if "system_settings" not in content:
    init_loc = content.find('safe_execute("CREATE TABLE IF NOT EXISTS company_closures')
    if init_loc != -1:
        insert_text = 'safe_execute("CREATE TABLE IF NOT EXISTS system_settings (key VARCHAR(50) PRIMARY KEY, value TEXT)")\n    '
        content = content[:init_loc] + insert_text + content[init_loc:]

# 2. Find tabs definition
old_tabs = 'tab_bennes, tab_catalogue, tab_fermetures = st.tabs(["🧰 Bennes", "🛒 Matériaux & Déchets", "📅 Fermetures"])'
new_tabs = 'tab_bennes, tab_catalogue, tab_fermetures, tab_ia = st.tabs(["🧰 Bennes", "🛒 Matériaux & Déchets", "📅 Fermetures", "🤖 Sécurité & I.A."])'

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    print("Tabs replaced.")

# 3. Add tab content at the end of the file (or end of Paramètres block)
# Let's find the end of the `elif navigation == "⚙️ Paramètres":` block. The file might end after it, or have an `else:` block.
# Actually, let's just insert it right before the final `else:` or at the EOF.
# Looking at the code structure, we can just find the end of the file if Paramètres is the last block, or we find a good anchor point.
