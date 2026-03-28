import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_prompt = '''                    # Construction du Prompt (Le vrai texte envoyé à l'IA)
                    prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles de manière logique.\\n\\n"

                    prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
" + df_pending_ai.to_string(index=False) + "

                    prompt += "👨✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
" + df_drivers_ai.to_string(index=False) + "

                    prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
" + df_vehicles_ai.to_string(index=False) + "

                    prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."'''

good_prompt = '''                    # Construction du Prompt (Le vrai texte envoyé à l'IA)
                    prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles de manière logique.\\n\\n"
                    prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                    prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                    prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                    prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."'''

if bad_prompt in content:
    content = content.replace(bad_prompt, good_prompt)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed strings 2")
else:
    print("Not found bad prompt")
    
# Try again with a more robust regex replacement if the exact string match fails
