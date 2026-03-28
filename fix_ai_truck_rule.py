import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver le prompt actuel
match = re.search(r'prompt = f"Tu es le DISPATCHEUR CHEF.*?prompt_user = prompt \+.*?\]" \n', content, re.DOTALL)

if match:
    old_prompt_block = match.group(0)
    
    # Remplacer la RÈGLE D'OR et ajouter la règle du camion unique par chauffeur
    new_prompt_block = old_prompt_block.replace(
        'prompt += "RÈGLE D\'OR : CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\n"',
        'prompt += "RÈGLES D\'OR :\\n1. CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\n2. UN CHAUFFEUR NE PEUT CONDUIRE QU\'UN SEUL ET UNIQUE CAMION POUR TOUTE SA TOURNÉE. (Ne fais pas changer de camion à un chauffeur entre deux livraisons).\\n"'
    )
    
    # Remplacer aussi dans le prompt system pour être sûr
    new_prompt_block = new_prompt_block.replace(
        "Tu dois répartir les commandes de manière logique (par ville) entre TOUS les chauffeurs.",
        "Tu dois répartir les commandes logiquement par ville. RÈGLE VITALE: Un chauffeur = Un seul camion pour toutes ses missions de la journée. Ne fais jamais changer un chauffeur de camion."
    )
    
    content = content.replace(old_prompt_block, new_prompt_block)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("AI truck rule injected.")
else:
    print("Could not find prompt block to update.")
