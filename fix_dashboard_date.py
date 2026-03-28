import re

with open("app.py", "r") as f:
    content = f.read()

old_dash_block = """if navigation == "📊 Tableau de bord":
    st.title("📊 Tableau de bord - Livraisons")
    query_orders = \"\"\"
        SELECT c.name as "Client", o.status as "Statut", 
            o.service_type as "Prestation", COALESCE(o.material, o.waste_type) as "Détails", 
            COALESCE(o.quantity_tons::text || ' T', o.container_type) as "Vol/Poids", 
            o.requested_date as "Date", COALESCE(o.requested_slot, 'Non spécifié') as "Créneau"
        FROM orders o LEFT JOIN clients c ON o.client_id = c.id
        ORDER BY o.requested_date DESC NULLS LAST LIMIT 50
    \"\"\"
    df_orders = load_data(query_orders)
    if not df_orders.empty:
        df_orders['Date'] = pd.to_datetime(df_orders['Date']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_orders, use_container_width=True, hide_index=True)"""

new_dash_block = """if navigation == "📊 Tableau de bord":
    st.title("📊 Tableau de bord - Livraisons")
    
    col_date, col_empty = st.columns([1, 3])
    with col_date:
        dash_date = st.date_input("Afficher les livraisons du :", datetime.date.today(), format="DD/MM/YYYY")
        
    query_orders = \"\"\"
        SELECT c.name as "Client", o.status as "Statut", 
            o.service_type as "Prestation", COALESCE(o.material, o.waste_type) as "Détails", 
            COALESCE(o.quantity_tons::text || ' T', o.container_type) as "Vol/Poids", 
            o.requested_date as "Date", COALESCE(o.requested_slot, 'Non spécifié') as "Créneau"
        FROM orders o LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.requested_date = :d
        ORDER BY o.created_at ASC
    \"\"\"
    df_orders = load_data(query_orders, {"d": dash_date})
    
    if not df_orders.empty:
        df_orders['Date'] = pd.to_datetime(df_orders['Date']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
    else:
        st.info(f"Aucune livraison prévue ou terminée pour le {dash_date.strftime('%d/%m/%Y')}.")"""

if old_dash_block in content:
    content = content.replace(old_dash_block, new_dash_block)
    print("Dashboard updated with date picker.")
else:
    print("Could not find the dashboard block.")

with open("app.py", "w") as f:
    f.write(content)

