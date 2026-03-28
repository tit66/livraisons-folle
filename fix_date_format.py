import re

with open("app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "st.date_input(" in line and "format=" not in line:
        # We need to insert format="DD/MM/YYYY" just before the closing parenthesis if possible, or append it to kwargs
        # A simple string replacement is safer since we know the structure
        lines[i] = re.sub(r'(st\.date_input\(.*?)\)', r'\1, format="DD/MM/YYYY")', line)

with open("app.py", "w") as f:
    f.writelines(lines)

