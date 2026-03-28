import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rename in sidebar
if '➕ Prise de Commande' in content:
    content = content.replace('➕ Prise de Commande', '📦 Gestion des Commandes')

# 2. Modify the section itself
start_str = 'elif navigation == "📦 Gestion des Commandes":'
if start_str in content:
    start_idx = content.find(start_str)
    
    # We need to wrap the whole Prise de Commande block into a tab
    # Find the next `elif navigation == `
    next_nav = content.find('elif navigation == ', start_idx + 10)
    
    block = content[start_idx:next_nav] if next_nav != -1 else content[start_idx:]
    
    # Let's see how the block starts. It has `st.title("➕ Nouvelle Commande")`
    title_str = '    st.title("➕ Nouvelle Commande")'
    if title_str in block:
        # Replace the title with tabs
        new_header = '''    st.title("📦 Gestion des Commandes")
    
    tab_new, tab_edit = st.tabs(["➕ Nouvelle Commande", "✏️ Modifier / Annuler une commande"])
    
    with tab_new:'''
        
        # Now we need to indent everything in tab_new. That's a bit tricky with python regex.
        # Alternatively, we can just put the title, tabs, and `with tab_new:` 
        # But indentation in python is strict.
        pass

