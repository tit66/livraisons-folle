with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line == '            try:\n' and 'if st.button("✅ Valider et Enregistrer"' in lines[i-1]:
        # This try is indented 12 spaces, but the code inside is indented 20.
        new_lines.append('                try:\n')
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
print("Fixed try indentation.")
