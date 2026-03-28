import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = 'prompt += "RÈGLE D\'OR N°1 : CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\nRÈGLE D\'OR N°2 : UN CHAUFFEUR NE DOIT AVOIR QU\'UN SEUL ET UNIQUE CAMION POUR TOUTE SA TOURNÉE DU JOUR. IL EST INTERDIT DE CHANGER DE CAMION EN COURS DE JOURNÉE.\\n"'
new1 = 'prompt += "RÈGLES LOGISTIQUES :\\n1. CHAQUE COMMANDE DOIT AVOIR UN CHAUFFEUR ET UN CAMION.\\n2. Un chauffeur PEUT changer de camion dans la journée si la mission l\'exige (ex: semi-remorque, puis 6x4 polybenne, puis 4x2 grue).\\n3. MINIMISE LES CHANGEMENTS INUTILES : Groupe les missions nécessitant le même camion pour un même chauffeur de façon consécutive.\\n"'

target2 = 'prompt_system = "Tu es un algorithme de dispatch logistique strict. Tu dois répartir les commandes de manière logique (par ville) entre TOUS les chauffeurs EN LEUR ATTRIBUANT UN SEUL CAMION POUR TOUTE LEUR TOURNÉE. Tu dois ABSOLUMENT retourner un tableau JSON'
new2 = 'prompt_system = "Tu es un algorithme de dispatch logistique strict. Tu dois répartir les commandes de manière logique (par ville et par type de matériel) entre TOUS les chauffeurs. Tu peux faire changer de camion un chauffeur si besoin, mais regroupe ses missions par type de camion pour éviter les allers-retours au dépôt. Tu dois ABSOLUMENT retourner un tableau JSON'

content = content.replace(target1, new1)
content = content.replace(target2, new2)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Flexible truck rules updated.")
