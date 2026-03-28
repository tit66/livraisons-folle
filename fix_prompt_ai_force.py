import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's completely rewrite the AI payload generation to force JSON schema using OpenAI structured outputs if possible
# Or just a much stronger prompt and lower temperature.

# The prompt was:
old_prompt = """prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles.\\n\\n"
                            prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                            prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                            prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                            prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."
                            
                            import requests
                            import json
                            
                            prompt_system = "Tu es un dispatcheur logistique expert (Tournées Bennes & Livraisons). Tu reçois des commandes, des chauffeurs et des camions. TA MISSION EST D'ASSIGNER TOUTES LES COMMANDES. AUCUNE COMMANDE NE DOIT ÊTRE OUBLIÉE. Répartis la charge de travail le plus équitablement possible entre TOUS les chauffeurs disponibles. Ne laisse aucun chauffeur vide. Optimise par ville si possible. Tu dois répondre UNIQUEMENT par un tableau JSON valide contenant TOUTES les commandes de la liste."
                            prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\"order_id\\": \\"uuid-ou-id\\", \\"driver_id\\": \\"uuid-ou-id\\", \\"vehicle_id\\": \\"uuid-ou-id\\"} ]\""""

# Let's find it. The format JSON expected string might be slightly different since my last replacements.
match = re.search(r'prompt = f"Tu es le dispatcheur principal.*?Format JSON exact attendu.*?"', content, re.DOTALL)

if match:
    new_prompt_code = """prompt = f"Tu es le DISPATCHEUR CHEF de l'entreprise. Tu as EXATEMENT {len(df_pending_ai)} commandes à planifier. AUCUNE EXCEPTION.\\n\\n"
                            prompt += "📦 COMMANDES À ASSIGNER (IL Y EN A " + str(len(df_pending_ai)) + ") :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                            prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES (ID, Prénom, Nom) :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                            prompt += "🚚 CAMIONS DISPONIBLES (ID, Plaque, Type) :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                            prompt += "RÈGLE D'OR : CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\n"
                            
                            import requests
                            import json
                            
                            prompt_system = "Tu es un algorithme de dispatch logistique strict. Tu dois répartir les commandes de manière logique (par ville) entre TOUS les chauffeurs. Tu dois ABSOLUMENT retourner un tableau JSON avec EXACTEMENT une ligne pour CHAQUE commande fournie dans le texte. Tu n'as pas le droit d'omettre une seule commande. Si tu reçois 10 commandes, le tableau JSON doit contenir 10 objets. Ne renvoie AUCUN texte en dehors du JSON pur."
                            prompt_user = prompt + "\\n\\nStructure exacte exigée pour ton résultat (JSON pur, sans bloc Markdown) :\\n[\\n  {\\"order_id\\": \\"l'id de la commande\\", \\"driver_id\\": \\"l'id du chauffeur choisi\\", \\"vehicle_id\\": \\"l'id du camion choisi\\"}\\n]" """
    
    content = content.replace(match.group(0), new_prompt_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Forced strict prompt injected.")
else:
    print("Could not find prompt code block.")
