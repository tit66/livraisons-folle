import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_old = """                    else:
                        st.info("Ici se trouvera l'appel HTTP (requests.post) vers l'API avec la clé. Pour l'instant on utilise le mode Prototype sans clé.")"""

target_new = """                    else:
                        import requests
                        import json
                        
                        prompt_system = "Tu es un dispatcheur logistique expert. Tu reçois des commandes, des chauffeurs et des camions. Tu dois assigner chaque commande à un chauffeur et un camion en répartissant la charge. Tu dois répondre UNIQUEMENT par un tableau JSON valide, sans aucun texte Markdown autour, sans balises ```json."
                        prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\\"order_id\\\": 1, \\\"driver_id\\\": 2, \\\"vehicle_id\\\": 3}, ... ]"
                        
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        data = {
                            "model": "gpt-4o-mini", # Modèle rapide et pas cher d'OpenAI
                            "messages": [
                                {"role": "system", "content": prompt_system},
                                {"role": "user", "content": prompt_user}
                            ],
                            "temperature": 0.1
                        }
                        
                        try:
                            # Appel direct à l'API OpenAI
                            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
                            
                            if response.status_code == 200:
                                result = response.json()
                                ai_text = result["choices"][0]["message"]["content"].strip()
                                
                                # Nettoyage si l'IA a quand même mis des balises Markdown
                                if ai_text.startswith("```json"):
                                    ai_text = ai_text[7:-3].strip()
                                elif ai_text.startswith("```"):
                                    ai_text = ai_text[3:-3].strip()
                                    
                                assignments = json.loads(ai_text)
                                
                                count = 0
                                for a in assignments:
                                    if "order_id" in a and "driver_id" in a and "vehicle_id" in a:
                                        run_query("UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                                  {"did": a["driver_id"], "vid": a["vehicle_id"], "oid": a["order_id"]})
                                        count += 1
                                        
                                st.success(f"🤖✅ Magie opérée ! {count} commandes assignées intelligemment par l'I.A.")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"Erreur de l'API OpenAI (Code {response.status_code}) : {response.text}")
                        except Exception as e:
                            st.error(f"Erreur lors de la communication avec l'IA ou de la lecture du JSON : {e}")"""

if target_old in content:
    content = content.replace(target_old, target_new)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Real AI module injected.")
else:
    print("Target not found.")
