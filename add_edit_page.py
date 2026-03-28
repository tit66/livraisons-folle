import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add to sidebar
old_nav = '["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "📍 Suivi des Bennes", "👥 Chauffeurs", "🚚 Flotte", "📱 Vue Chauffeur (Mobile)", "⚙️ Paramètres"]'
new_nav = '["📊 Tableau de bord", "➕ Prise de Commande", "📅 Planning", "✏️ Édition Commandes", "📍 Suivi des Bennes", "👥 Chauffeurs", "🚚 Flotte", "📱 Vue Chauffeur (Mobile)", "⚙️ Paramètres"]'

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    print("Sidebar updated.")

# 2. Add the page itself
# We can inject it right before `elif navigation == "📍 Suivi des Bennes":`
target = 'elif navigation == "📍 Suivi des Bennes":'
if target in content:
    edit_page_code = """elif navigation == "✏️ Édition Commandes":
    st.title("✏️ Édition & Annulation des Commandes")
    st.write("Modifiez la date, passez une commande en devis, ou annulez-la définitivement.")
    
    # Récupérer les commandes modifiables (pending, attente_devis, planned)
    query_edit = \"\"\"
        SELECT o.id, c.name as client_name, o.service_type, COALESCE(o.dropoff_address, 'Adresse Inconnue') as address, 
               o.requested_date, o.status 
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.id
        WHERE o.status IN ('pending', 'attente_devis', 'planned')
        ORDER BY o.requested_date ASC
    \"\"\"
    df_edit = load_data(query_edit)
    
    if df_edit.empty:
        st.success("Aucune commande en cours à modifier.")
    else:
        # Création d'un dictionnaire pour le selectbox
        dict_orders = {}
        for _, r in df_edit.iterrows():
            status_emoji = "⏳" if r['status'] == 'pending' else "📝" if r['status'] == 'attente_devis' else "✅"
            dict_orders[r['id']] = f"{status_emoji} {pd.to_datetime(r['requested_date']).strftime('%d/%m')} - {r['client_name']} ({r['service_type']}) - {r['address']}"
            
        order_to_edit = st.selectbox("Sélectionnez la commande à modifier :", options=[None] + list(dict_orders.keys()), format_func=lambda x: "--- Choisir une commande ---" if x is None else dict_orders[x])
        
        if order_to_edit:
            st.divider()
            
            df_order_details = df_edit[df_edit['id'] == order_to_edit].iloc[0]
            current_date = pd.to_datetime(df_order_details['requested_date']).date()
            current_status = df_order_details['status']
            
            st.write(f"### Détails de la commande N° {order_to_edit}")
            st.write(f"**Client :** {df_order_details['client_name']}")
            st.write(f"**Type :** {df_order_details['service_type'].upper()} - {df_order_details['address']}")
            
            with st.form(f"edit_form_{order_to_edit}"):
                c1, c2 = st.columns(2)
                with c1:
                    import datetime as dt
                    new_date = st.date_input("📅 Décaler la Date", value=current_date)
                with c2:
                    status_options = {"pending": "⏳ En attente (Prêt pour Planning)", "attente_devis": "📝 Attente de devis (Bloqué)", "planned": "✅ Planifié", "cancelled": "❌ Annulé"}
                    new_status = st.selectbox("Statut de la commande", options=list(status_options.keys()), index=list(status_options.keys()).index(current_status), format_func=lambda x: status_options[x])
                
                if st.form_submit_button("💾 Enregistrer les modifications", type="primary"):
                    # Si on passe de planned à autre chose, on désassigne
                    extra_query = ", driver_id = NULL, vehicle_id = NULL, trailer_id = NULL " if current_status == 'planned' and new_status != 'planned' else ""
                    
                    run_query(f"UPDATE orders SET requested_date = :nd, status = :ns {extra_query} WHERE id = :oid", {"nd": new_date, "ns": new_status, "oid": order_to_edit})
                    st.success("Modifications enregistrées avec succès !")
                    import time
                    time.sleep(1)
                    st.rerun()

"""
    content = content.replace(target, edit_page_code + target)
    print("Page Edition injected.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

