import re

with open("app.py", "r") as f:
    content = f.read()

old_query = """        SELECT c.id as client_id, c.name as client_name, s.label as site_label, o.container_type as size, 
               SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 
                        WHEN o.service_type = 'Benne - Enlèvement' THEN -1 
                        ELSE 0 END) as net_bennes
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        LEFT JOIN sites s ON o.site_id = s.id
        WHERE o.service_type LIKE 'Benne %'
        GROUP BY c.id, c.name, s.label, o.container_type
        HAVING SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' THEN -1 ELSE 0 END) > 0"""

new_query = """        SELECT c.id as client_id, c.name as client_name, s.label as site_label, 
               COALESCE(s.address, c.billing_address) as address, 
               s.gmaps_link as gmaps_link, o.container_type as size, 
               SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 
                        WHEN o.service_type = 'Benne - Enlèvement' THEN -1 
                        ELSE 0 END) as net_bennes
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        LEFT JOIN sites s ON o.site_id = s.id
        WHERE o.service_type LIKE 'Benne %'
        GROUP BY c.id, c.name, s.label, COALESCE(s.address, c.billing_address), s.gmaps_link, o.container_type
        HAVING SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' THEN -1 ELSE 0 END) > 0"""

if old_query in content:
    content = content.replace(old_query, new_query)
else:
    print("Could not find query")

old_display = """    with col_d:
        if not df_pos.empty and selected_client:
            st.write("### 📍 Détail par Chantier")
            # Create visual cards for each site
            for _, row in df_client_bennes.iterrows():
                site_name = row['site_label'] if row['site_label'] else "Adresse principale"
                with st.container():
                    st.markdown(f"**Chantier : {site_name}**")
                    st.markdown(f"🧰 **{row['net_bennes']} x Benne {row['size']}**")
                    st.divider()"""

new_display = """    with col_d:
        if not df_pos.empty and selected_client:
            st.write("### 📍 Détail par Chantier")
            for _, row in df_client_bennes.iterrows():
                site_name = row['site_label'] if row['site_label'] else "Adresse principale"
                address = row['address'] if pd.notna(row['address']) else "Adresse non renseignée"
                
                # Lien Google Maps : Soit le gmaps_link renseigné, soit une recherche sur l'adresse texte
                if pd.notna(row['gmaps_link']) and row['gmaps_link'].strip() != "":
                    gmaps_url = row['gmaps_link']
                else:
                    import urllib.parse
                    safe_address = urllib.parse.quote(address)
                    gmaps_url = f"https://www.google.com/maps/search/?api=1&query={safe_address}"
                
                with st.container():
                    st.markdown(f"#### 🏗️ Chantier : {site_name}")
                    st.markdown(f"**Adresse :** {address}")
                    st.markdown(f"**Volume posé :** 🧰 **{row['net_bennes']} x Benne {row['size']}**")
                    st.markdown(f"[🗺️ Ouvrir dans Google Maps]({gmaps_url})")
                    st.divider()"""

if old_display in content:
    content = content.replace(old_display, new_display)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success replacing display")
else:
    print("Could not find display")

