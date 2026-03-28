import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver le début du bloc "Assistant de Pré-assignation par I.A."
start_str = '    with st.expander("🧠 Assistant de Pré-assignation par I.A.", expanded=True):'
start_idx = content.find(start_str)

if start_idx != -1:
    # On va chercher la fin du bloc (le elif suivant ou query_pending juste en dessous du block si j'ai injecté au début ?)
    # Oups, j'ai injecté au début de la page Planning. La fin du bloc if (le bloc AI) se termine avant query_pending
    end_str = '    query_pending = """'
    end_idx = content.find(end_str, start_idx)
    
    if end_idx != -1:
        old_block = content[start_idx:end_idx]
        
        new_block = """    with st.expander("🧠 Assistant de Pré-assignation par I.A.", expanded=True):
        st.write("L'I.A. analyse les adresses, les types de bennes et les horaires pour créer un brouillon de tournée optimisée.")
        
        # Récupérer la clé API depuis la DB
        api_key_df = load_data("SELECT value FROM system_settings WHERE key = 'openai_api_key'")
        api_key = api_key_df.iloc[0]['value'] if not api_key_df.empty else ""
        
        if not api_key:
            st.warning("⚠️ Veuillez configurer votre clé API OpenAI dans l'onglet **⚙️ Paramètres** pour utiliser cette fonction.")
        else:
            if "ai_proposal" not in st.session_state:
                if st.button("✨ Demander une proposition de tournées", type="primary", use_container_width=True):
                    with st.spinner("L'I.A. réfléchit à la meilleure répartition..."):
                        import time
                        time.sleep(1.5)
                        
                        query_ai_orders = "SELECT o.id, c.name as client_name, o.service_type, o.dropoff_address, o.waste_type FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.requested_date = :d AND o.status = 'pending'"
                        df_pending_ai = load_data(query_ai_orders, {"d": date_planning})
                        df_drivers_ai = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
                        df_vehicles_ai = load_data("SELECT id, license_plate, type FROM vehicles WHERE is_available = true")
                        
                        if df_pending_ai.empty:
                            st.warning("Aucune commande en attente pour cette date.")
                        elif df_drivers_ai.empty or df_vehicles_ai.empty:
                            st.error("Veuillez vous assurer d'avoir au moins un chauffeur et un camion actifs.")
                        else:
                            prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles.\\n\\n"
                            prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                            prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                            prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                            prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."
                            
                            import requests
                            import json
                            
                            prompt_system = "Tu es un dispatcheur logistique expert. Tu reçois des commandes, des chauffeurs et des camions. Tu dois assigner chaque commande à un chauffeur et un camion. Tu dois répondre UNIQUEMENT par un tableau JSON valide."
                            prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\\"order_id\\\": 1, \\\"driver_id\\\": 2, \\\"vehicle_id\\\": 3} ]"
                            
                            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                            data = {
                                "model": "gpt-4o-mini",
                                "messages": [{"role": "system", "content": prompt_system}, {"role": "user", "content": prompt_user}],
                                "temperature": 0.1
                            }
                            
                            try:
                                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
                                if response.status_code == 200:
                                    result = response.json()
                                    ai_text = result["choices"][0]["message"]["content"].strip()
                                    if ai_text.startswith("```json"): ai_text = ai_text[7:-3].strip()
                                    elif ai_text.startswith("```"): ai_text = ai_text[3:-3].strip()
                                        
                                    assignments = json.loads(ai_text)
                                    st.session_state["ai_proposal"] = assignments
                                    st.rerun()
                                else:
                                    st.error(f"Erreur API (Code {response.status_code}) : {response.text}")
                            except Exception as e:
                                st.error(f"Erreur de lecture : {e}")

            if "ai_proposal" in st.session_state:
                st.success("✅ Voici la proposition de l'I.A. :")
                
                df_d = load_data("SELECT id, first_name, last_name FROM drivers")
                dict_d = {row['id']: f"{row['first_name']} {row['last_name']}" for _, row in df_d.iterrows()}
                df_v = load_data("SELECT id, license_plate FROM vehicles")
                dict_v = {row['id']: row['license_plate'] for _, row in df_v.iterrows()}
                
                ids = ','.join([str(a.get('order_id', 0)) for a in st.session_state['ai_proposal']])
                df_o = load_data(f"SELECT o.id, c.name, o.service_type, o.dropoff_address FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id IN ({ids})") if ids else pd.DataFrame()
                
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    if not df_o.empty and o_id in df_o['id'].values:
                        order_info = df_o[df_o['id'] == o_id].iloc[0]
                        preview_data.append({
                            "Commande N°": o_id,
                            "Client": order_info['name'],
                            "Type": order_info['service_type'],
                            "Chauffeur Prévu": dict_d.get(a.get("driver_id"), "Inconnu"),
                            "Camion Prévu": dict_v.get(a.get("vehicle_id"), "Inconnu")
                        })
                
                if preview_data:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
                
                col_val, col_cancel = st.columns(2)
                with col_val:
                    if st.button("✅ Valider et Assigner", type="primary", use_container_width=True):
                        count = 0
                        for a in st.session_state["ai_proposal"]:
                            if "order_id" in a and "driver_id" in a and "vehicle_id" in a:
                                run_query("UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                          {"did": a["driver_id"], "vid": a["vehicle_id"], "oid": a["order_id"]})
                                count += 1
                        del st.session_state["ai_proposal"]
                        st.success(f"Opération terminée : {count} commandes validées et assignées !")
                        import time
                        time.sleep(2)
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Refuser (Annuler)", use_container_width=True):
                        del st.session_state["ai_proposal"]
                        st.rerun()

"""
        content = content.replace(old_block, new_block)
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Done. Replaced the whole block.")
    else:
        print("End query_pending not found.")
else:
    print("Start block not found.")
