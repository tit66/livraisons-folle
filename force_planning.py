import re

with open("app.py", "r") as f:
    content = f.read()

# Instead of exact replace, find where "elif navigation == "📅 Planning":" starts, and replace until the next "elif navigation =="
import re

pattern = re.compile(r'elif navigation == "📅 Planning":.*?elif navigation == "📍 Suivi des Bennes":', re.DOTALL)

new_plan = """elif navigation == "📅 Planning":
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
        
        selected_order_ids = []
        for idx, row in df_pending.iterrows():
            label = f"📦 **N° {row['id']} - {row['client_name']}** | {row['service_type']} | {row['qty']} ({row['details']}) | 🕒 {row['requested_slot']}"
            if st.checkbox(label, key=f"chk_{row['id']}"):
                selected_order_ids.append(row['id'])
                
        st.divider()
        st.write("### 2️⃣ Assigner les ressources à la sélection")
        
        df_chauffeurs = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true ORDER BY first_name")
        dict_chauffeurs = {None: "(Sélectionner un chauffeur)"}
        if not df_chauffeurs.empty:
            for _, r in df_chauffeurs.iterrows(): dict_chauffeurs[r['id']] = f"{r['first_name']} {r['last_name']}"
            
        df_vehicules = load_data("SELECT id, license_plate, brand_model, vehicle_type FROM vehicles WHERE is_active = true ORDER BY vehicle_type")
        dict_camions = {None: "(Sélectionner un camion)"}
        dict_remorques = {None: "(Aucune remorque)"}
        if not df_vehicules.empty:
            for _, r in df_vehicules.iterrows():
                label = f"{r['license_plate']} - {r['brand_model']} ({r['vehicle_type']})"
                dict_camions[r['id']] = label
                dict_remorques[r['id']] = label
        
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
                        "t_id": selected_trailer,
                        "ids": selected_order_ids
                    })
                    st.success(f"🎉 {len(selected_order_ids)} commande(s) assignée(s) avec succès à {dict_chauffeurs[selected_driver]} !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur SQL lors de l'assignation : {e}")

elif navigation == "📍 Suivi des Bennes":"""

if pattern.search(content):
    content = pattern.sub(new_plan, content)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success regex")
else:
    print("Regex failed")
