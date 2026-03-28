import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'prompt += "🚚 CAMIONS DISPONIBLES (ID, Plaque, Type) :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"'
new_target = """prompt += "🚚 CAMIONS DISPONIBLES (ID, Plaque, Type) :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"
                            prompt += "MÉTHODE DE SÉLECTION DU CAMION SELON LE TYPE DE COMMANDE :\\n"
                            prompt += "- Pour la pose, le retrait ou la rotation de bennes, utilise un camion de type 'benne' ou 'ampliroll'.\\n"
                            prompt += "- Pour des livraisons de matériaux spécifiques ou accès difficiles (Big Bags), préfère un camion 'grue'.\\n"
                            prompt += "- Assure-toi que les correspondances matériel/véhicule aient du sens techniquement.\\n\\n\""""

content = content.replace(target, new_target)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated matching instructions.")
