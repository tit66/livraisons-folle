with open("app.py", "r") as f:
    lines = f.readlines()

for i in range(440, 465):
    print(repr(lines[i]))

