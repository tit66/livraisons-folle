import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# On va chercher la partie depuis "# Construction du Prompt" jusqu'à "Règle :"
match = re.search(r'# Construction du Prompt.*?Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."', content, re.DOTALL)

if match:
    old_text = match.group(0)
    new_text = '''# Construction du Prompt (Le vrai texte envoyé à l'IA)
                    prompt = f"Tu es le dispatcheur principal. Assigne ces {len(df_pending_ai)} commandes aux chauffeurs et camions disponibles de manière logique.\\n\\n"
                    prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"
                    prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"
                    prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                    prompt += "Règle : Répartis la charge équitablement. Retourne uniquement un tableau JSON."'''
    
    content = content.replace(old_text, new_text)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed via regex.")
else:
    print("Not found via regex.")
