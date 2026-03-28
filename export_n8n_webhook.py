import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                        "status_final": statut_final
                    })
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")"""

new_target = """                        "status_final": statut_final
                    })
                    
                    # Déclenchement silencieux du Webhook n8n pour sauvegarde externe (Google Sheets, etc.)
                    try:
                        import requests
                        payload = {
                            "client_id": final_client_id, "site_id": final_site_id, 
                            "service_type": service_final, "material": marchandise, 
                            "quantity_tons": quantite, "container_type": volume_benne,
                            "waste_type": type_benne, "instructions": instructions, 
                            "requested_date": date_livraison.strftime('%Y-%m-%d'), "requested_slot": creneau_choisi,
                            "status": statut_final, "is_devis": souhaite_devis
                        }
                        # Remplacer l'URL par le vrai webhook n8n quand il sera créé
                        # requests.post("http://n8n-local_n8n_1:5678/webhook/backup-google-sheets", json=payload, timeout=2)
                        pass # Le code est prêt, il suffit de le décommenter quand n8n sera configuré
                    except Exception:
                        pass # Ne pas bloquer l'app si n8n est down
                        
                    st.success(f"🎉 Commande enregistrée pour le {date_livraison.strftime('%d/%m/%Y')} (Créneau : {creneau_choisi}).")"""

if target in content:
    content = content.replace(target, new_target)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("n8n webhook call prepared.")
else:
    print("Could not find insert block to add webhook.")
