import re

with open("app.py", "r") as f:
    content = f.read()

content = content.replace("match = re.search", "match = regex.search")

with open("app.py", "w") as f:
    f.write(content)
print("Fixed regex call.")

