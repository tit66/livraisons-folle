with open("app.py", "r") as f:
    content = f.read()

content = content.replace("if navigation != \"⚙️ Paramètres\":\n\n\n", "")
with open("app.py", "w") as f:
    f.write(content)
