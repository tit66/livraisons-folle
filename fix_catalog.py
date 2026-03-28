import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update Prise de Commande for Materials
old_mat = 'marchandise = st.selectbox("Type de marchandise", ["Sable", "Gravier", "Terre végétale", "Mélange béton"])'
new_mat = """df_mat = load_data("SELECT name FROM catalog_items WHERE category='material' ORDER BY name")
                list_mat = df_mat['name'].tolist() if not df_mat.empty else ["Sable", "Gravier", "Terre végétale", "Mélange béton"]
                marchandise = st.selectbox("Type de marchandise", list_mat)"""
content = content.replace(old_mat, new_mat)

# 2. Update Prise de Commande for Waste
old_waste = 'type_benne = st.selectbox("Type de déchets", ["Gravats", "DIB (Tout venant)", "Déchets verts", "Bois"])'
new_waste = """df_waste = load_data("SELECT name FROM catalog_items WHERE category='waste' ORDER BY name")
                list_waste = df_waste['name'].tolist() if not df_waste.empty else ["Gravats", "DIB (Tout venant)", "Déchets verts", "Bois"]
                type_benne = st.selectbox("Type de déchets", list_waste)"""
content = content.replace(old_waste, new_waste)

# 3. Add Catalog Tab to Settings
old_tabs = 'tab_bennes, tab_fermetures = st.tabs(["🧰 Stock de Bennes (Capital)", "📅 Fermetures & Jours Fériés"])'
new_tabs = 'tab_bennes, tab_catalogue, tab_fermetures = st.tabs(["🧰 Bennes", "🛒 Matériaux & Déchets", "📅 Fermetures"])'
content = content.replace(old_tabs, new_tabs)

catalog_tab_content = """    with tab_catalogue:
        st.write("### 🛒 Catalogue : Matériaux & Déchets")
        st.write("Ajoutez ou supprimez les types de marchandises et de déchets qui apparaissent dans le formulaire de commande.")
        
        c_cat1, c_cat2 = st.columns(2)
        
        with c_cat1:
            st.subheader("Matériaux (Livraisons)")
            df_mat = load_data("SELECT id, name FROM catalog_items WHERE category='material' ORDER BY name")
            st.dataframe(df_mat.drop(columns=['id']) if not df_mat.empty else df_mat, hide_index=True, use_container_width=True)
            
            with st.form("add_mat_form"):
                new_mat_name = st.text_input("Nouveau Matériau")
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if new_mat_name:
                        run_query("INSERT INTO catalog_items (category, name) VALUES ('material', :n) ON CONFLICT DO NOTHING", {"n": new_mat_name})
                        st.rerun()
            
            with st.form("del_mat_form"):
                mat_to_del = st.selectbox("Supprimer un matériau :", options=df_mat['name'].tolist() if not df_mat.empty else [])
                if st.form_submit_button("❌ Supprimer"):
                    if mat_to_del:
                        run_query("DELETE FROM catalog_items WHERE category='material' AND name=:n", {"n": mat_to_del})
                        st.rerun()

        with c_cat2:
            st.subheader("Déchets (Bennes)")
            df_waste = load_data("SELECT id, name FROM catalog_items WHERE category='waste' ORDER BY name")
            st.dataframe(df_waste.drop(columns=['id']) if not df_waste.empty else df_waste, hide_index=True, use_container_width=True)
            
            with st.form("add_waste_form"):
                new_waste_name = st.text_input("Nouveau type de Déchet")
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if new_waste_name:
                        run_query("INSERT INTO catalog_items (category, name) VALUES ('waste', :n) ON CONFLICT DO NOTHING", {"n": new_waste_name})
                        st.rerun()
            
            with st.form("del_waste_form"):
                waste_to_del = st.selectbox("Supprimer un déchet :", options=df_waste['name'].tolist() if not df_waste.empty else [])
                if st.form_submit_button("❌ Supprimer"):
                    if waste_to_del:
                        run_query("DELETE FROM catalog_items WHERE category='waste' AND name=:n", {"n": waste_to_del})
                        st.rerun()

"""

# Inject before tab_fermetures
content = content.replace('    with tab_fermetures:', catalog_tab_content + '\n    with tab_fermetures:')

with open("app.py", "w") as f:
    f.write(content)

