with open("app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "except Exception as e:" in line:
        # Check surrounding lines to see indentation level
        print(f"Line {i-2}: {repr(lines[i-2])}")
        print(f"Line {i-1}: {repr(lines[i-1])}")
        print(f"Line {i}: {repr(line)}")
        print(f"Line {i+1}: {repr(lines[i+1])}")
        
        # Replace the bad indent with the correct one
        lines[i] = "                except Exception as e:\n"
        lines[i+1] = "                    st.error(f\"Erreur SQL globale : {e}\")\n"

with open("app.py", "w") as f:
    f.writelines(lines)
    
print("Updated.")
