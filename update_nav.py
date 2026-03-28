import os

with open("app.py", "r") as f:
    content = f.read()

# 1. Update navigation menu
content = content.replace(
    'navigation = st.sidebar.radio("Navigation", ["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "⚙️ Paramètres"])',
    'navigation = st.sidebar.radio("Navigation", ["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "👥 Chauffeurs", "⚙️ Paramètres"])'
)

# 2. Extract Chauffeurs from Paramètres and create its own block
old_param_block = """elif navigation == "⚙️ Paramètres":
    st.title("⚙️ Paramètres & Ressources")
    tab_chauffeurs, tab_vehicules, tab_conges = st.tabs(["👥 Chauffeurs", "🚚 Flotte (Véhicules)", "📅 Fermetures"])
    
    with tab_chauffeurs:"""

new_param_block = """elif navigation == "👥 Chauffeurs":
    st.title("👥 Gestion des Chauffeurs")"""

content = content.replace(old_param_block, new_param_block)

# 3. Fix indentation
lines = content.split('\n')
new_lines = []
in_chauffeur = False

for line in lines:
    if line.startswith('elif navigation == "👥 Chauffeurs":'):
        in_chauffeur = True
        new_lines.append(line)
        continue
        
    if in_chauffeur and line.startswith('    with tab_vehicules:'):
        in_chauffeur = False
        new_lines.append('elif navigation == "⚙️ Paramètres":')
        new_lines.append('    st.title("⚙️ Paramètres & Ressources")')
        new_lines.append('    tab_vehicules, tab_conges = st.tabs(["🚚 Flotte (Véhicules)", "📅 Fermetures"])')
        new_lines.append('    with tab_vehicules:')
        continue

    if in_chauffeur:
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

