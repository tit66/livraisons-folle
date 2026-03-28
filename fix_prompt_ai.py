import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt_system = """prompt_system = "Tu es un dispatcheur logistique expert. Tu reçois des commandes, des chauffeurs et des camions. Tu dois assigner chaque commande à un chauffeur et un camion. Tu dois répondre UNIQUEMENT par un tableau JSON valide."
                            prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\"order_id\\": 1, \\"driver_id\\": 2, \\"vehicle_id\\": 3} ]\""""

new_prompt_system = """prompt_system = "Tu es un dispatcheur logistique expert (Tournées Bennes & Livraisons). Tu reçois des commandes, des chauffeurs et des camions. TA MISSION EST D'ASSIGNER TOUTES LES COMMANDES. AUCUNE COMMANDE NE DOIT ÊTRE OUBLIÉE. Répartis la charge de travail le plus équitablement possible entre TOUS les chauffeurs disponibles. Ne laisse aucun chauffeur vide. Optimise par ville si possible. Tu dois répondre UNIQUEMENT par un tableau JSON valide contenant TOUTES les commandes de la liste."
                            prompt_user = prompt + "\\nFormat JSON exact attendu : [ {\\"order_id\\": 1, \\"driver_id\\": 2, \\"vehicle_id\\": 3} ]\""""

if old_prompt_system in content:
    content = content.replace(old_prompt_system, new_prompt_system)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Prompt AI system improved.")
else:
    print("Prompt system string not matched. Trying with regex.")

