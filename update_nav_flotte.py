import os

with open("app.py", "r") as f:
    content = f.read()

# 1. Update navigation menu
content = content.replace(
    'navigation = st.sidebar.radio("Navigation", ["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "👥 Chauffeurs", "⚙️ Paramètres"])',
    'navigation = st.sidebar.radio("Navigation", ["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "👥 Chauffeurs", "🚚 Flotte", "⚙️ Paramètres"])'
)

# 2. Extract Flotte from Paramètres and create its own block
old_param_block = """elif navigation == "⚙️ Paramètres":
    st.title("⚙️ Paramètres & Ressources")
    tab_vehicules, tab_conges = st.tabs(["🚚 Flotte (Véhicules)", "📅 Fermetures"])
    with tab_vehicules:"""

new_param_block = """elif navigation == "🚚 Flotte":
    st.title("🚚 Flotte (Véhicules)")"""

content = content.replace(old_param_block, new_param_block)

# 3. Fix indentation
lines = content.split('\n')
new_lines = []
in_flotte = False

for line in lines:
    if line.startswith('elif navigation == "🚚 Flotte":'):
        in_flotte = True
        new_lines.append(line)
        continue
        
    if in_flotte and line.startswith('    with tab_conges:'):
        in_flotte = False
        new_lines.append('elif navigation == "⚙️ Paramètres":')
        new_lines.append('    st.title("⚙️ Paramètres & Fermetures")')
        continue

    if in_flotte:
        # Desindent by 4 spaces
        if line.startswith('        '):
            new_lines.append(line[4:])
        elif line.startswith('    '):
            new_lines.append(line) # title line
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.write('\n'.join(new_lines))

