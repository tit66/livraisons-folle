with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line == '                else:\n' and '*(Aucun lien GPS spécifique enregistré pour ce chantier)*' in lines[i+1]:
        new_lines.append('            else:\n')
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
    
print("Fixed else.")
