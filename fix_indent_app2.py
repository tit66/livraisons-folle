with open("app.py", "r") as f:
    content = f.read()

old_block2 = '''                            INSERT INTO sites (client_id, label, address, gmaps_link, is_active) 
                            VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                    """, {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                        final_site_id = res[0]'''

new_block2 = '''                            INSERT INTO sites (client_id, label, address, gmaps_link, is_active) 
                            VALUES (:cid, :lbl, :addr, :gmaps, true) RETURNING id
                        """, {"cid": final_client_id, "lbl": lbl, "addr": new_site_address, "gmaps": new_site_gmaps}).fetchone()
                        if res: final_site_id = res[0]'''

if old_block2 in content:
    content = content.replace(old_block2, new_block2)
    with open("app.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Could not find block 2")

