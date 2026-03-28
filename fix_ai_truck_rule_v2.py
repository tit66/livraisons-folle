import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'prompt += "RÈGLE D\'OR : CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\n"'
new_target = 'prompt += "RÈGLE D\'OR N°1 : CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\nRÈGLE D\'OR N°2 : UN CHAUFFEUR NE DOIT AVOIR QU\'UN SEUL ET UNIQUE CAMION POUR TOUTE SA TOURNÉE DU JOUR. IL EST INTERDIT DE CHANGER DE CAMION EN COURS DE JOURNÉE.\\n"'

content = content.replace(target, new_target)

target_sys = 'prompt_system = "Tu es un algorithme de dispatch logistique strict. Tu dois répartir les commandes de manière logique (par ville) entre TOUS les chauffeurs. Tu dois ABSOLUMENT retourner un tableau JSON'
new_sys = 'prompt_system = "Tu es un algorithme de dispatch logistique strict. Tu dois répartir les commandes de manière logique (par ville) entre TOUS les chauffeurs EN LEUR ATTRIBUANT UN SEUL CAMION POUR TOUTE LEUR TOURNÉE. Tu dois ABSOLUMENT retourner un tableau JSON'

content = content.replace(target_sys, new_sys)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rules updated.")
