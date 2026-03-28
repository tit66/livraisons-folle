import os

with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
in_param = False

for line in lines:
    if line.startswith('elif navigation == "⚙️ Paramètres":'):
        in_param = True
        new_lines.append(line)
        continue

    if in_param:
        if line.startswith('    with tab_conges:'):
            continue # Skip this line
        elif line.startswith('        '):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
