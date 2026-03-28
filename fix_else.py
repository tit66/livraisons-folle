import re

with open("app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line == "            try:\n" and lines[i-1].strip() == "else:":
        print(f"Replacing line {i}")
        lines[i] = "                try:\n"

with open("app.py", "w") as f:
    f.writelines(lines)
    
print("Fixed.")
