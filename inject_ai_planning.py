import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1))'

ai_block = """    date_planning = st.date_input("Date du planning à préparer", dt.date.today() + dt.timedelta(days=1))
    
    st.divider()
    with st.expander("🧠 Assistant de Pré-assignation par I.A.", expanded=True):
        st.write("L'I.A. analyse les adresses, les types de bennes et les horaires pour créer un brouillon de tournée optimisée.")
        api_key = st.text_input("Clé API OpenAI / Gemini (Laisser vide pour le mode Prototype Rapide)", type="password")
        
        if st.button("✨ Lancer l'optimisation des tournées", type="primary", use_container_width=True):
            with st.spinner("L'I.A. réfléchit à la meilleure répartition..."):
                import time
                time.sleep(1.5) # Effet visuel
                
                # Récupération des données pour l'IA
                query_ai_orders = "SELECT o.id, c.name, o.service_type, o.dropoff_address, o.waste_type FROM orders o LEFT JOIN clients c ON o.client_id = c.id WHERE o.requested_date = :d AND o.status = 'pending'"
                df_pending_ai = load_data(query_ai_orders, {"d": date_planning})
                df_drivers_ai = load_data("SELECT id, first_name, last_name FROM drivers WHERE is_active = true")
                df_vehicles_ai = load_data("SELECT id, license_plate, type FROM vehicles WHERE is_available = true")
                
                if df_pending_ai.empty:
                    st.warning("Aucune commande en 'pending' pour cette date.")
                elif df_drivers_ai.empty or df_vehicles_ai.empty:
                    st.error("Veuillez vous assurer d'avoir au moins un chauffeur et un camion actifs.")
                else:
                    # Construction du Prompt (Le vrai texte envoyé à l'IA)
                    prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles de manière logique.\n\n"
                    prompt += "📦 COMMANDES À ASSIGNER :\n" + df_pending_ai.to_string(index=False) + "\n\n"
                    prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\n" + df_drivers_ai.to_string(index=False) + "\n\n"
                    prompt += "🚚 CAMIONS DISPONIBLES :\n" + df_vehicles_ai.to_string(index=False) + "\n\n"
                    prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."
                    
                    st.code(prompt, language="text") # Affiche le prompt généré pour Thierry
                    
                    if not api_key:
                        # Prototype : Algorithme de base qui simule la réponse de l'IA
                        d_ids = df_drivers_ai['id'].tolist()
                        v_ids = df_vehicles_ai['id'].tolist()
                        # Création de la flotte dispo (1 chauffeur = 1 camion)
                        fleet = [{"d": d_ids[i], "v": v_ids[i]} for i in range(min(len(d_ids), len(v_ids)))]
                        
                        for idx, row in df_pending_ai.iterrows():
                            assignee = fleet[idx % len(fleet)]
                            run_query("UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid", 
                                      {"did": assignee["d"], "vid": assignee["v"], "oid": row['id']})
                        
                        st.success(f"✅ Succès ! {len(df_pending_ai)} commandes ont été assignées. (Mode Prototype)")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.info("Ici se trouvera l'appel HTTP (requests.post) vers l'API avec la clé. Pour l'instant on utilise le mode Prototype sans clé.")"""

if target in content:
    content = content.replace(target, ai_block)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("AI module injected.")
else:
    print("Target not found.")
