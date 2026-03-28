with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('            try:'):
        if 'est_valide, message_erreur' in lines[lines.index(line)+1]:
            # This is the first try
            new_lines.append(line)
        else:
            # This is the bad try
            new_lines.append('                try:\n')
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
