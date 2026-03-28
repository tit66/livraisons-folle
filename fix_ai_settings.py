import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Check if system_settings table exists
if 'CREATE TABLE IF NOT EXISTS system_settings' not in content:
    init_loc = content.find('safe_execute("CREATE TABLE IF NOT EXISTS company_closures')
    if init_loc != -1:
        insert_text = 'safe_execute("CREATE TABLE IF NOT EXISTS system_settings (key VARCHAR(50) PRIMARY KEY, value TEXT)")\n    '
        content = content[:init_loc] + insert_text + content[init_loc:]

# 2. Update tabs
old_tabs = 'tab_bennes, tab_catalogue, tab_fermetures = st.tabs(["🧰 Bennes", "🛒 Matériaux & Déchets", "📅 Fermetures"])'
new_tabs = 'tab_bennes, tab_catalogue, tab_fermetures, tab_ia = st.tabs(["🧰 Bennes", "🛒 Matériaux & Déchets", "📅 Fermetures", "🤖 Sécurité & I.A."])'

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)

# 3. Add AI tab content at the end of the file (since fermetures is the last block)
if 'with tab_ia:' not in content:
    ai_block = """

    with tab_ia:
        st.write("### 🤖 Configuration I.A. & Accès API")
        st.write("Section sécurisée pour la configuration des algorithmes intelligents.")
        
        pin_ia = st.text_input("Code PIN Administrateur requis :", type="password", key="pin_ia")
        
        if pin_ia == "2026": 
            st.success("Accès Sécurisé Déverrouillé 🔓")
            
            # Fetch current key
            current_key_df = load_data("SELECT value FROM system_settings WHERE key = 'openai_api_key'")
            current_key = current_key_df.iloc[0]['value'] if not current_key_df.empty else ""
            
            with st.form("ai_settings_form"):
                new_api_key = st.text_input("Clé API OpenAI (sk-...)", value=current_key, type="password", help="Utilisée pour la pré-assignation intelligente des tournées au Dispatch.")
                if st.form_submit_button("💾 Enregistrer la clé", type="primary"):
                    run_query("INSERT INTO system_settings (key, value) VALUES ('openai_api_key', :v) ON CONFLICT (key) DO UPDATE SET value = :v", {"v": new_api_key})
                    st.success("✅ Clé API sauvegardée en base de données avec succès !")
                    st.rerun()
        elif pin_ia:
            st.error("❌ Code PIN incorrect.")
"""
    content += ai_block

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Settings AI tab added.")
