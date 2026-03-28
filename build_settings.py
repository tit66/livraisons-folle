import re

with open("app.py", "r") as f:
    content = f.read()

old_settings_block = """elif navigation == "⚙️ Paramètres":
    st.title("⚙️ Paramètres & Fermetures")
    st.subheader("➕ Ajouter une fermeture")
    st.info("Le formulaire des fermetures est ici.")"""

new_settings_block = """elif navigation == "⚙️ Paramètres":
    st.title("⚙️ Paramètres de l'Entreprise")
    
    tab_bennes, tab_fermetures = st.tabs(["🧰 Stock de Bennes (Capital)", "📅 Fermetures & Jours Fériés"])
    
    with tab_bennes:
        st.write("### 📊 Inventaire Global (Ce que possède l'entreprise)")
        st.caption("Attention : Ceci modifie le stock physique total (ex: en cas d'achat, de vol ou de casse définitive), pas l'assignation chez les clients.")
        
        df_inv = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
        if not df_inv.empty:
            df_inv.columns = ["Volume de la Benne", "Quantité Totale Possédée"]
            st.dataframe(df_inv, use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("### 🔒 Modification Sécurisée")
            pin = st.text_input("Code PIN Administrateur requis pour modifier :", type="password")
            
            # Code PIN simple pour le MVP (à changer en prod ou mettre dans un .env)
            if pin == "2026": 
                st.success("Accès Admin Déverrouillé 🔓")
                
                with st.form("edit_inventory_form"):
                    st.write("Mettre à jour les quantités totales :")
                    
                    # Create columns for the form
                    col1, col2 = st.columns(2)
                    new_counts = {}
                    
                    for i, row in df_inv.iterrows():
                        size = row["Volume de la Benne"]
                        current = row["Quantité Totale Possédée"]
                        # Alternate columns
                        with col1 if i % 2 == 0 else col2:
                            new_counts[size] = st.number_input(f"Bennes {size} (Ajustement total)", min_value=0, value=current, step=1)
                            
                    if st.form_submit_button("💾 Enregistrer le nouveau stock", type="primary"):
                        try:
                            for s, c in new_counts.items():
                                run_query("UPDATE skip_inventory SET total_count = :c WHERE size = :s", {"c": c, "s": s})
                            st.success("✅ Stock global mis à jour avec succès !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
            elif pin != "":
                st.error("❌ Code PIN incorrect.")
        else:
            st.warning("Aucun inventaire initialisé dans la base de données.")
            
    with tab_fermetures:
        st.write("### 📅 Jours de fermeture de l'entreprise")
        st.info("Module en construction (à relier au calendrier).")
"""

if old_settings_block in content:
    content = content.replace(old_settings_block, new_settings_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Settings updated successfully!")
else:
    print("Failed to replace settings block.")

