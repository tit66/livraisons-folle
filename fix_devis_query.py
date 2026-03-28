import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_query_block = """                    insert_query = \"\"\"
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) 
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, 'pending', 'admin_streamlit', :req_date, :req_slot)
                    \"\"\"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    run_query(insert_query, {
                        "client_id": final_client_id, "site_id": final_site_id, "service_type": service_final,
                        "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                        "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi
                    })"""

new_query_block = """                    insert_query = \"\"\"
                    INSERT INTO orders (client_id, site_id, service_type, material, quantity_tons, container_type, waste_type, instructions, status, source, requested_date, requested_slot) 
                    VALUES (:client_id, :site_id, :service_type, :material, :quantity, :container_type, :waste_type, :instructions, :status_final, 'admin_streamlit', :req_date, :req_slot)
                    \"\"\"
                    service_final = f"Benne - {action_benne}" if prestation == "Location de benne" else prestation
                    statut_final = "attente_devis" if souhaite_devis else "pending"
                    run_query(insert_query, {
                        "client_id": final_client_id, "site_id": final_site_id, "service_type": service_final,
                        "material": marchandise, "quantity": quantite, "container_type": volume_benne,
                        "waste_type": type_benne, "instructions": instructions, "req_date": date_livraison, "req_slot": creneau_choisi,
                        "status_final": statut_final
                    })"""

if old_query_block in content:
    content = content.replace(old_query_block, new_query_block)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Devis query fixed.")
else:
    print("Not found devis query.")
