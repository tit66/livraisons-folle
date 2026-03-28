with open("app.py", "r") as f:
    content = f.read()

# Make sure the block is executed safely for KPI
old_kpi = """    df_pos = load_data(query_pos)
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
                    st.divider()"""

# Just checking if code runs
