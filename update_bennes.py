import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update init_connection to add skip_inventory table
old_init_end = """        CREATE TABLE IF NOT EXISTS vehicles (
            id SERIAL PRIMARY KEY, license_plate VARCHAR(50) UNIQUE, vehicle_type VARCHAR(100), brand_model VARCHAR(150), 
            next_technical_inspection DATE, next_tachograph_inspection DATE, next_speed_limiter_inspection DATE, 
            is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")
    
    return engine"""

new_init_end = """        CREATE TABLE IF NOT EXISTS vehicles (
            id SERIAL PRIMARY KEY, license_plate VARCHAR(50) UNIQUE, vehicle_type VARCHAR(100), brand_model VARCHAR(150), 
            next_technical_inspection DATE, next_tachograph_inspection DATE, next_speed_limiter_inspection DATE, 
            is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")
    
    safe_execute(\"\"\"
        CREATE TABLE IF NOT EXISTS skip_inventory (
            size VARCHAR(20) PRIMARY KEY,
            total_count INT DEFAULT 0
        )
    \"\"\")
    # Initialize skip sizes if empty
    safe_execute("INSERT INTO skip_inventory (size, total_count) VALUES ('8m3', 10), ('10m3', 15), ('15m3', 5), ('30m3', 5) ON CONFLICT DO NOTHING")
    
    return engine"""

if old_init_end in content:
    content = content.replace(old_init_end, new_init_end)
else:
    print("Failed to update init_connection")


# 2. Update Suivi des Bennes logic
old_suivi = """elif navigation == "📍 Suivi des Bennes":
    st.title("📍 Suivi du Parc de Bennes")
    st.write("Où sont nos bennes actuellement ?")
    st.info("Bientôt : Liste des bennes posées chez les clients pour organiser les rotations et enlèvements.")"""

new_suivi = """elif navigation == "📍 Suivi des Bennes":
    st.title("📍 Suivi du Parc de Bennes")
    
    # Load total inventory
    df_inv = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
    total_bennes_flotte = int(df_inv['total_count'].sum()) if not df_inv.empty else 0
    
    # Calculate skips currently at clients (based on orders : Pose = +1, Enlevement = -1)
    # We consider orders that are not pending/cancelled. For now, we count all 'Pose' vs 'Enlevement'
    query_pos = \"\"\"
        SELECT c.id as client_id, c.name as client_name, s.label as site_label, o.container_type as size, 
               SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 
                        WHEN o.service_type = 'Benne - Enlèvement' THEN -1 
                        ELSE 0 END) as net_bennes
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        LEFT JOIN sites s ON o.site_id = s.id
        WHERE o.service_type LIKE 'Benne %'
        GROUP BY c.id, c.name, s.label, o.container_type
        HAVING SUM(CASE WHEN o.service_type = 'Benne - Pose' THEN 1 WHEN o.service_type = 'Benne - Enlèvement' THEN -1 ELSE 0 END) > 0
    \"\"\"
    df_pos = load_data(query_pos)
    total_chez_clients = int(df_pos['net_bennes'].sum()) if not df_pos.empty else 0
    total_au_depot = total_bennes_flotte - total_chez_clients
    
    # Visual KPI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric(label="📦 TOTAL BENNES FLOTTE", value=total_bennes_flotte)
    c2.metric(label="🏗️ BENNES CHEZ LES CLIENTS", value=total_chez_clients)
    c3.metric(label="🏢 BENNES DISPO (DÉPÔT)", value=total_au_depot)
    
    st.divider()
    
    col_g, col_d = st.columns([1, 2])
    with col_g:
        st.write("### 👥 Visualisation par Client")
        if df_pos.empty:
            st.info("Aucune benne actuellement posée chez les clients.")
        else:
            # Dropdown to select client from those who have skips
            client_list = df_pos['client_name'].unique()
            selected_client = st.selectbox("Sélectionner un client pour voir le détail :", client_list)
            
            df_client_bennes = df_pos[df_pos['client_name'] == selected_client]
            total_client = int(df_client_bennes['net_bennes'].sum())
            st.success(f"**{selected_client}** a actuellement **{total_client} benne(s)** en cours de location.")
            
    with col_d:
        if not df_pos.empty and selected_client:
            st.write("### 📍 Détail par Chantier")
            # Create visual cards for each site
            for _, row in df_client_bennes.iterrows():
                site_name = row['site_label'] if row['site_label'] else "Adresse principale"
                with st.container():
                    st.markdown(f"**Chantier : {site_name}**")
                    st.markdown(f"🧰 **{row['net_bennes']} x Benne {row['size']}**")
                    st.divider()
"""

if old_suivi in content:
    content = content.replace(old_suivi, new_suivi)
else:
    print("Failed to update Suivi")

# 3. Update Paramètres to add Bennes inventory management
old_param_tabs = """tab_chauffeurs, tab_vehicules, tab_conges = st.tabs(["👥 Chauffeurs", "🚚 Flotte (Véhicules)", "📅 Fermetures"])"""
new_param_tabs = """tab_chauffeurs, tab_vehicules, tab_bennes, tab_conges = st.tabs(["👥 Chauffeurs", "🚚 Flotte (Camions)", "🗑️ Parc Bennes", "📅 Fermetures"])"""
content = content.replace(old_param_tabs, new_param_tabs)

# Insert the new tab_bennes content
tab_conges_block = """    with tab_conges:
        st.subheader("➕ Ajouter une fermeture")"""

tab_bennes_block = """    with tab_bennes:
        st.subheader("🗑️ Gestion du Parc de Bennes")
        st.write("Mettez à jour le nombre total de bennes que vous possédez (suite à un achat, un vol, ou une destruction).")
        
        df_inv = load_data("SELECT size, total_count FROM skip_inventory ORDER BY size")
        if not df_inv.empty:
            for _, row in df_inv.iterrows():
                col_b1, col_b2, col_b3 = st.columns([2, 2, 4])
                with col_b1:
                    st.markdown(f"#### Benne {row['size']}")
                with col_b2:
                    new_val = st.number_input(f"Total possédé ({row['size']})", value=int(row['total_count']), min_value=0, key=f"inv_{row['size']}")
                with col_b3:
                    st.write("")
                    st.write("")
                    if st.button(f"💾 Sauvegarder ({row['size']})", key=f"btn_inv_{row['size']}"):
                        run_query("UPDATE skip_inventory SET total_count = :cnt WHERE size = :sz", {"cnt": new_val, "sz": row['size']})
                        st.success("Inventaire mis à jour !")
                        st.rerun()
                st.divider()

    with tab_conges:
        st.subheader("➕ Ajouter une fermeture")"""

content = content.replace(tab_conges_block, tab_bennes_block)

with open("app.py", "w") as f:
    f.write(content)
print("Done")

