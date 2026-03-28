import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ajouter la table settings dans init_connection
if "system_settings" not in content:
    init_loc = content.find('safe_execute("CREATE TABLE IF NOT EXISTS company_closures')
    if init_loc != -1:
        insert_text = 'safe_execute("CREATE TABLE IF NOT EXISTS system_settings (key VARCHAR(50) PRIMARY KEY, value TEXT)")\n    '
        content = content[:init_loc] + insert_text + content[init_loc:]
        print("Settings table added to init.")

# 2. Modifier la page Paramètres
param_loc = content.find('elif navigation == "⚙️ Paramètres":')
if param_loc != -1:
    param_end_loc = content.find('else:', param_loc) # Ou la fin du fichier
    
    # Check if AI section already exists
    if "🤖 Configuration I.A." not in content[param_loc:]:
        new_param_section = """elif navigation == "⚙️ Paramètres":
    st.title("⚙️ Paramètres")
    
    st.write("### 🤖 Configuration I.A.")
    current_key_df = load_data("SELECT value FROM system_settings WHERE key = 'openai_api_key'")
    current_key = current_key_df.iloc[0]['value'] if not current_key_df.empty else ""
    
    with st.form("ai_settings_form"):
        new_api_key = st.text_input("Clé API OpenAI (sk-...)", value=current_key, type="password", help="Utilisée pour la pré-assignation intelligente des tournées.")
        if st.form_submit_button("💾 Enregistrer la clé"):
            run_query("INSERT INTO system_settings (key, value) VALUES ('openai_api_key', :v) ON CONFLICT (key) DO UPDATE SET value = :v", {"v": new_api_key})
            st.success("Clé API sauvegardée !")
            st.rerun()
            
    st.divider()
"""
        content = content.replace('elif navigation == "⚙️ Paramètres":\n    st.title("⚙️ Paramètres")', new_param_section)
        print("Parameters page updated.")

# 3. Mettre à jour la section Planning
old_ai_block = re.search(r'    with st.expander\("🧠 Assistant de Pré-assignation par I.A.".*?(st.success\("🎉.*?|st.error\("Erreur lors de la communication.*?\n)', content, re.DOTALL)

if old_ai_block:
    new_ai_block = """    with st.expander("🧠 Assistant de Pré-assignation par I.A.", expanded=True):
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
                            # Construction du Prompt
                            prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles.\\n\\n"
                            prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                            prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                            prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                            prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."
                            
                            import requests
                            import json
                            
                            prompt_system = "Tu es un dispatcheur logistique expert. Tu reçois des commandes, des chauffeurs et des camions. Tu dois assigner chaque commande à un chauffeur et un camion. Tu dois répondre UNIQUEMENT par un tableau JSON valide."
                            prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\\"order_id\\\": 1, \\\"driver_id\\\": 2, \\\"vehicle_id\\\": 3}, ... ]"
                            
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
                                    # Sauvegarde dans le state pour validation
                                    st.session_state["ai_proposal"] = assignments
                                    st.rerun()
                                else:
                                    st.error(f"Erreur API (Code {response.status_code}) : {response.text}")
                            except Exception as e:
                                st.error(f"Erreur lors de la lecture de la réponse : {e}")

            if "ai_proposal" in st.session_state:
                st.success("✅ Voici la proposition de l'I.A. :")
                
                # Fetch reference data to display names instead of IDs
                df_d = load_data("SELECT id, first_name, last_name FROM drivers")
                dict_d = {row['id']: f"{row['first_name']} {row['last_name']}" for _, row in df_d.iterrows()}
                df_v = load_data("SELECT id, license_plate FROM vehicles")
                dict_v = {row['id']: row['license_plate'] for _, row in df_v.iterrows()}
                df_o = load_data(f"SELECT o.id, c.name, o.service_type, o.dropoff_address FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.id IN ({','.join([str(a.get('order_id', 0)) for a in st.session_state['ai_proposal']])})") if st.session_state['ai_proposal'] else pd.DataFrame()
                
                # Create a nice preview table
                preview_data = []
                for a in st.session_state["ai_proposal"]:
                    o_id = a.get("order_id")
                    order_info = df_o[df_o['id'] == o_id].iloc[0] if not df_o.empty and o_id in df_o['id'].values else None
                    if order_info is not None:
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
                        st.rerun()"""
    
    # Remplacement sécurisé
    content = content[:old_ai_block.start()] + new_ai_block + content[old_ai_block.end():]
    print("Planning AI block updated with preview mode.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
