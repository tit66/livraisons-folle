with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.startswith('                with st.container():'):
        print(f"Replacing line {i}")
        new_lines.append('                with st.container():\n')
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
