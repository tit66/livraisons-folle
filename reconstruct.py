#!/usr/bin/env python3
"""
Reconstruction script for app.py
Applies all add_*.py and fix_*.py scripts in chronological order (by mtime)
to produce app_reconstructed.py
"""

import os
import sys
import shutil
import subprocess
import tempfile
import glob

BASE_DIR = "/home/thierry/workspace/livraisons-app"
APP_PY = os.path.join(BASE_DIR, "app.py")
APP_RECONSTRUCTED = os.path.join(BASE_DIR, "app_reconstructed.py")

# 1. Initialize: copy app.py → app_reconstructed.py
print("[INIT] Copying app.py → app_reconstructed.py")
shutil.copy2(APP_PY, APP_RECONSTRUCTED)
print(f"[INIT] Done. Size: {os.path.getsize(APP_RECONSTRUCTED)} bytes")

# 2. List and sort scripts by modification time (oldest first)
patterns = [
    os.path.join(BASE_DIR, "add_*.py"),
    os.path.join(BASE_DIR, "fix_*.py"),
]
scripts = []
for pattern in patterns:
    scripts.extend(glob.glob(pattern))

# Sort by mtime ascending (oldest first)
scripts.sort(key=lambda f: os.path.getmtime(f))

print(f"\n[SCRIPTS] Found {len(scripts)} scripts to apply:")
for s in scripts:
    print(f"  - {os.path.basename(s)}")

# 3. Apply each script
failed = []
succeeded = []

with tempfile.TemporaryDirectory() as tmpdir:
    for script_path in scripts:
        script_name = os.path.basename(script_path)
        print(f"\n[APPLY] {script_name}")
        
        # Copy current app_reconstructed.py → tmpdir/app.py
        tmp_app = os.path.join(tmpdir, "app.py")
        shutil.copy2(APP_RECONSTRUCTED, tmp_app)
        
        # Also copy the script to tmpdir
        tmp_script = os.path.join(tmpdir, script_name)
        shutil.copy2(script_path, tmp_script)
        
        # Read script to check what it does
        with open(script_path, "r") as f:
            script_content = f.read()
        
        # Run the script in tmpdir
        result = subprocess.run(
            [sys.executable, tmp_script],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  [WARNING] {script_name} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"  STDERR: {result.stderr[:500]}")
            failed.append((script_name, f"exit code {result.returncode}: {result.stderr[:200]}"))
            # Don't update app_reconstructed.py, keep previous version
        else:
            # Check if tmp app.py was modified
            if os.path.exists(tmp_app):
                new_size = os.path.getsize(tmp_app)
                old_size = os.path.getsize(APP_RECONSTRUCTED)
                shutil.copy2(tmp_app, APP_RECONSTRUCTED)
                print(f"  [OK] Applied. Size: {old_size} → {new_size} bytes")
                succeeded.append(script_name)
            else:
                print(f"  [WARNING] {script_name} ran OK but app.py is missing in tmpdir")
                failed.append((script_name, "app.py missing after run"))

# 4. Syntax check
print("\n[SYNTAX CHECK]")
check_result = subprocess.run(
    [sys.executable, "-c", f"import ast; ast.parse(open('{APP_RECONSTRUCTED}').read()); print('Syntax OK')"],
    capture_output=True,
    text=True
)

if check_result.returncode == 0:
    syntax_ok = True
    print("  ✅ Syntax OK!")
else:
    syntax_ok = False
    print(f"  ❌ Syntax ERROR: {check_result.stderr}")

# 5. Final report
print("\n" + "="*60)
print("RAPPORT FINAL")
print("="*60)
print("Reconstruction terminée.")
print(f"Le fichier est disponible à : {APP_RECONSTRUCTED}")
print(f"  Taille finale : {os.path.getsize(APP_RECONSTRUCTED)} bytes")
print(f"  Scripts appliqués avec succès : {len(succeeded)}/{len(scripts)}")

if failed:
    print(f"\n  ⚠️  Scripts qui n'ont pas pu être appliqués ({len(failed)}):")
    for name, reason in failed:
        print(f"    - {name}: {reason}")
else:
    print("\n  ✅ Tous les scripts ont été appliqués avec succès!")

print(f"\n  Contrôle de syntaxe : {'✅ OK' if syntax_ok else '❌ ERREUR'}")
if not syntax_ok:
    print(f"  Détail: {check_result.stderr}")
