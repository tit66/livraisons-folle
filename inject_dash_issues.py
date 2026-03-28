import re

with open("app.py", "r") as f:
    content = f.read()

old_dash_block = """    # ENCART ALERTES
    alerts = check_alerts()
    if alerts:
        st.divider()
        st.warning("### ⚠️ Rappels & Échéances (Chauffeurs & Flotte)")
        for a in alerts:
            st.markdown(f"- {a}")"""

new_dash_block = """    # ENCART ALERTES
    alerts = check_alerts()
    if alerts:
        st.divider()
        st.warning("### ⚠️ Rappels & Échéances (Chauffeurs & Flotte)")
        for a in alerts:
            st.markdown(f"- {a}")
            
    # ALERTES PROBLEMES VEHICULES
    df_issues = load_data("SELECT vi.id, d.first_name, d.last_name, v.license_plate, vi.description, vi.created_at, vi.photo_data FROM vehicle_issues vi JOIN drivers d ON vi.driver_id = d.id JOIN vehicles v ON vi.vehicle_id = v.id WHERE vi.is_resolved = false ORDER BY vi.created_at DESC")
    if not df_issues.empty:
        st.divider()
        st.error("### 🚨 Signalements Problèmes Véhicules")
        for idx, row in df_issues.iterrows():
            date_str = pd.to_datetime(row['created_at']).strftime('%d/%m/%Y %H:%M')
            with st.expander(f"⚠️ {row['license_plate']} - Signalé par {row['first_name']} {row['last_name']} le {date_str}", expanded=True):
                st.write(f"**Description :** {row['description']}")
                if pd.notna(row['photo_data']) and row['photo_data'].strip() != "":
                    import base64
                    st.image(base64.b64decode(row['photo_data']), caption="Photo du problème", width=300)
                
                if st.button("✅ Marquer comme Résolu", key=f"resolve_issue_{row['id']}"):
                    run_query("UPDATE vehicle_issues SET is_resolved = true WHERE id = :id", {"id": row['id']})
                    st.rerun()"""

if old_dash_block in content:
    content = content.replace(old_dash_block, new_dash_block)
    with open("app.py", "w") as f:
        f.write(content)
    print("Dashboard updated with vehicle issues!")
else:
    print("Failed to replace dashboard block.")
