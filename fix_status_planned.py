import re

with open("app.py", "r") as f:
    content = f.read()

# Replace 'assigned' with 'planned' in Planning logic
content = content.replace("status = 'assigned'", "status = 'planned'")

with open("app.py", "w") as f:
    f.write(content)
print("Updated assigned to planned in app.py")
