import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """            row_v = load_data(f"SELECT * FROM vehicles WHERE id = '{edit_v_id}'").iloc[0]
            with st.form("edit_v"):
                st.write(f"Modification de {row_v['license_plate']}")
                new_ct = st.date_input("Fin CT", value=row_v['control_valid_until'], format="DD/MM/YYYY")
                new_chrono = st.date_input("Fin Chrono", value=row_v['tachograph_valid_until'] if pd.notna(row_v['tachograph_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                new_limiteur = st.date_input("Fin Limiteur", value=row_v['speed_limiter_valid_until'] if pd.notna(row_v['speed_limiter_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                if st.form_submit_button("💾 Mettre à jour"):
                    run_query("UPDATE vehicles SET control_valid_until=:ct, tachograph_valid_until=:ch, speed_limiter_valid_until=:li WHERE id=:id",
                              {"ct": new_ct, "ch": new_chrono, "li": new_limiteur, "id": edit_v_id})
                    st.success("Mis à jour !")
                    st.rerun()"""

new_block = """            row_v = load_data(f"SELECT * FROM vehicles WHERE id = '{edit_v_id}'").iloc[0]
            with st.form("edit_v"):
                st.write(f"Modification de {row_v['license_plate']}")
                
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    new_ct = st.date_input("Fin CT", value=row_v['control_valid_until'], format="DD/MM/YYYY")
                    new_chrono = st.date_input("Fin Chrono", value=row_v['tachograph_valid_until'] if pd.notna(row_v['tachograph_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                with c_v2:
                    new_limiteur = st.date_input("Fin Limiteur", value=row_v['speed_limiter_valid_until'] if pd.notna(row_v['speed_limiter_valid_until']) else datetime.date.today(), format="DD/MM/YYYY")
                    is_available = st.checkbox("✅ Véhicule Disponible (Décocher s'il est au garage/en réparation)", value=bool(row_v['is_available']))
                
                if st.form_submit_button("💾 Mettre à jour", type="primary"):
                    run_query("UPDATE vehicles SET control_valid_until=:ct, tachograph_valid_until=:ch, speed_limiter_valid_until=:li, is_available=:avail WHERE id=:id",
                              {"ct": new_ct, "ch": new_chrono, "li": new_limiteur, "avail": is_available, "id": edit_v_id})
                    st.success("Mis à jour !")
                    st.rerun()"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Vehicle edit block updated with is_available.")
else:
    print("Could not find the vehicle edit block.")

# Update the list display to show the availability status
old_list_block = """            if not df_v.empty:
                df_v.columns = ["ID", "Nom", "Marque", "Modèle", "Immat", "Remorqueur/Notes", "Fin CT", "Fin Chrono", "Fin Limiteur"]
                st.dataframe(df_v.drop(columns=['ID']), use_container_width=True, hide_index=True)"""

new_list_block = """            df_v = load_data(f"SELECT id, name, brand, model, license_plate, is_available, maintenance_notes, control_valid_until, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE type='{t}'")
            if not df_v.empty:
                df_v.columns = ["ID", "Nom", "Marque", "Modèle", "Immat", "Dispo", "Remorqueur/Notes", "Fin CT", "Fin Chrono", "Fin Limiteur"]
                
                # Format the Dispo column for better visual feedback
                df_v['Dispo'] = df_v['Dispo'].apply(lambda x: "✅ Oui" if x else "❌ Au garage")
                
                st.dataframe(df_v.drop(columns=['ID']), use_container_width=True, hide_index=True)"""

# I need to find the loop where df_v is generated to inject the new query and columns
import re
pattern = re.compile(r'df_v = load_data\(f"SELECT id, name, brand, model, license_plate, maintenance_notes, control_valid_until, tachograph_valid_until, speed_limiter_valid_until FROM vehicles WHERE type=\'{t}\'"\)\n\s+if not df_v\.empty:\n\s+df_v\.columns = \["ID", "Nom", "Marque", "Modèle", "Immat", "Remorqueur/Notes", "Fin CT", "Fin Chrono", "Fin Limiteur"\]\n\s+st\.dataframe\(df_v\.drop\(columns=\[\'ID\'\]\), use_container_width=True, hide_index=True\)')

content = pattern.sub(new_list_block, content)

with open("app.py", "w") as f:
    f.write(content)
print("List display updated!")
