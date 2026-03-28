import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip().startswith('prompt = f"Tu es le dispatcheur principal'):
        new_lines.append(f'                    prompt = f"Tu es le dispatcheur principal. Assigne ces {{len(df_pending_ai)}} commandes aux chauffeurs et camions disponibles de manière logique.\\n\\n"\n')
        # On va sauter les lignes cassées
    elif line.strip() == '"':
        pass # Ignorer les guillemets de fin cassés
    elif line.strip().startswith('prompt += "📦 COMMANDES À ASSIGNER :'):
        new_lines.append('                    prompt += "📦 COMMANDES À ASSIGNER :\\n" + df_pending_ai.to_string(index=False) + "\\n\\n"\n')
    elif line.strip().startswith('prompt += "👨✈️ CHAUFFEURS DISPONIBLES :'):
        new_lines.append('                    prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"\n')
    elif line.strip().startswith('prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :'):
        new_lines.append('                    prompt += "👨‍✈️ CHAUFFEURS DISPONIBLES :\\n" + df_drivers_ai.to_string(index=False) + "\\n\\n"\n')
    elif line.strip().startswith('prompt += "🚚 CAMIONS DISPONIBLES :'):
        new_lines.append('                    prompt += "🚚 CAMIONS DISPONIBLES :\\n" + df_vehicles_ai.to_string(index=False) + "\\n\\n"\n')
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Strings fixed.")
