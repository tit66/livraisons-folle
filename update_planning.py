import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update the init_connection to add driver_id, vehicle_id, trailer_id to orders
old_init = """    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_number VARCHAR(100)")
    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")"""

new_init = """    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_number VARCHAR(100)")
    safe_execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS driver_card_expiry DATE")
    
    safe_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS driver_id INT")
    safe_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS vehicle_id INT")
    safe_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS trailer_id INT")"""

if old_init in content:
    content = content.replace(old_init, new_init)

# 2. Update the Planning section
old_planning = """elif navigation == "📅 Planning":
    st.title("📅 Planning & Assignation")
    st.write("Assignez les commandes en attente aux chauffeurs et véhicules.")
    
    import datetime as dt
    date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1), format="DD/MM/YYYY")
    
    query_pending = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.material, o.waste_type) as details, 
               COALESCE(o.quantity_tons::text || ' T', o.container_type) as qty, o.requested_slot, o.status
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d AND o.status IN ('pending', 'assigned')
        ORDER BY o.requested_slot ASC
    \"\"\"
    df_pending = load_data(query_pending, {"d": date_planning})
    
    if df_pending.empty:
        st.success(f"Aucune commande en attente pour le {date_planning.strftime('%d/%m/%Y')}.")
    else:
        st.write(f"### Commandes pour le {date_planning.strftime('%d/%m/%Y')} ({len(df_pending)} à traiter)")
        
        df_chauffeurs = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
        chauffeurs_list = ["(Non assigné)"]
        if not df_chauffeurs.empty:
            chauffeurs_list.extend([f"{r['first_name']} {r['last_name']}" for _, r in df_chauffeurs.iterrows()])
            
        df_vehicules = load_data("SELECT license_plate, brand_model FROM vehicles WHERE is_active = true")
        vehicules_list = ["(Non assigné)"]
        if not df_vehicules.empty:
            vehicules_list.extend([f"{r['license_plate']} - {r['brand_model']}" for _, r in df_vehicules.iterrows()])
        
        for idx, row in df_pending.iterrows():
            with st.container():
                st.markdown(f"**N° {row['id']} - {row['client_name']}** | {row['service_type']} | {row['qty']} ({row['details']}) | 🕒 {row['requested_slot']}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    chauffeur = st.selectbox(f"Chauffeur", chauffeurs_list, key=f"chauf_{row['id']}")
                with col2:
                    camion = st.selectbox(f"Véhicule", vehicules_list, key=f"cam_{row['id']}")
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("💾 Assigner", key=f"btn_{row['id']}", type="primary"):
                        st.success(f"Commande {row['id']} assignée à {chauffeur} ({camion}).")
                st.divider()"""

new_planning = """elif navigation == "📅 Planning":
    st.title("📅 Planning & Assignation")
    st.write("Cochez les commandes à grouper, puis assignez-leur un chauffeur, un camion et une remorque.")
    
    import datetime as dt
    date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1), format="DD/MM/YYYY")
    
    query_pending = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.material, o.waste_type) as details, 
               COALESCE(o.quantity_tons::text || ' T', o.container_type) as qty, o.requested_slot, o.status
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d AND o.status IN ('pending', 'assigned')
        ORDER BY o.requested_slot ASC
    \"\"\"
    df_pending = load_data(query_pending, {"d": date_planning})
    
    if df_pending.empty:
        st.success(f"Aucune commande en attente pour le {date_planning.strftime('%d/%m/%Y')}.")
    else:
        st.write(f"### 1️⃣ Sélectionner les commandes du {date_planning.strftime('%d/%m/%Y')} ({len(df_pending)} en attente)")
        
        # Checkboxes for orders
        selected_order_ids = []
        for idx, row in df_pending.iterrows():
            label = f"📦 **N° {row['id']} - {row['client_name']}** | {row['service_type']} | {row['qty']} ({row['details']}) | 🕒 {row['requested_slot']}"
            if st.checkbox(label, key=f"chk_{row['id']}"):
                selected_order_ids.append(row['id'])
                
        st.divider()
        st.write("### 2️⃣ Assigner les ressources à la sélection")
        
        # Load active drivers
        df_chauffeurs = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true ORDER BY first_name")
        dict_chauffeurs = {None: "(Sélectionner un chauffeur)"}
        if not df_chauffeurs.empty:
            for _, r in df_chauffeurs.iterrows(): dict_chauffeurs[r['id']] = f"{r['first_name']} {r['last_name']}"
            
        # Load active vehicles
        df_vehicules = load_data("SELECT id, license_plate, brand_model, vehicle_type FROM vehicles WHERE is_active = true ORDER BY vehicle_type")
        dict_camions = {None: "(Sélectionner un camion)"}
        dict_remorques = {None: "(Aucune remorque)"}
        if not df_vehicules.empty:
            for _, r in df_vehicules.iterrows():
                label = f"{r['license_plate']} - {r['brand_model']} ({r['vehicle_type']})"
                dict_camions[r['id']] = label
                dict_remorques[r['id']] = label # We can use any vehicle as trailer, or filter later
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_driver = st.selectbox("👨‍✈️ Chauffeur", options=list(dict_chauffeurs.keys()), format_func=lambda x: dict_chauffeurs[x])
        with col2:
            selected_truck = st.selectbox("🚚 Camion", options=list(dict_camions.keys()), format_func=lambda x: dict_camions[x])
        with col3:
            selected_trailer = st.selectbox("🔗 Remorque (Optionnel)", options=list(dict_remorques.keys()), format_func=lambda x: dict_remorques[x])
            
        st.write("")
        if st.button("💾 Assigner la sélection", type="primary", use_container_width=True):
            if not selected_order_ids:
                st.error("⚠️ Veuillez cocher au moins une commande dans la liste au-dessus.")
            elif not selected_driver or not selected_truck:
                st.error("⚠️ Veuillez sélectionner au moins un chauffeur et un camion.")
            else:
                try:
                    # Update database for all selected orders
                    update_query = \"\"\"
                        UPDATE orders 
                        SET status = 'assigned', 
                            driver_id = :d_id, 
                            vehicle_id = :v_id, 
                            trailer_id = :t_id 
                        WHERE id = ANY(:ids)
                    \"\"\"
                    run_query(update_query, {
                        "d_id": selected_driver,
                        "v_id": selected_truck,
                        "t_id": selected_trailer, # Can be None
                        "ids": selected_order_ids
                    })
                    st.success(f"🎉 {len(selected_order_ids)} commande(s) assignée(s) avec succès à {dict_chauffeurs[selected_driver]} !")
                    st.rerun() # Refresh page to show updated list
                except Exception as e:
                    st.error(f"Erreur SQL lors de l'assignation : {e}")"""

if old_planning in content:
    content = content.replace(old_planning, new_planning)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Could not find planning block")

