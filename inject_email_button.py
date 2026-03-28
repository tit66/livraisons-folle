import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                col_val, col_cancel = st.columns(2)
                with col_val:
                    if st.button("✅ Valider et Assigner", type="primary", use_container_width=True):
                        count = 0
                        for a in st.session_state["ai_proposal"]:
                            if "order_id" in a and "driver_id" in a and "vehicle_id" in a:
                                run_query("UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                          {"did": a["driver_id"], "vid": a["vehicle_id"], "oid": a["order_id"]})
                                count += 1
                        del st.session_state["ai_proposal"]
                        st.success(f"Opération terminée : {count} commandes validées et assignées !")
                        import time
                        time.sleep(2)
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Refuser (Annuler)", use_container_width=True):
                        del st.session_state["ai_proposal"]
                        st.rerun()"""

new_block = """                col_val, col_email, col_cancel = st.columns(3)
                with col_val:
                    if st.button("✅ Valider et Assigner", type="primary", use_container_width=True):
                        count = 0
                        for a in st.session_state["ai_proposal"]:
                            if "order_id" in a and "driver_id" in a and "vehicle_id" in a:
                                run_query("UPDATE orders SET status='planned', driver_id=:did, vehicle_id=:vid WHERE id=:oid",
                                          {"did": a["driver_id"], "vid": a["vehicle_id"], "oid": a["order_id"]})
                                count += 1
                        del st.session_state["ai_proposal"]
                        st.success(f"Opération terminée : {count} commandes validées et assignées !")
                        import time
                        time.sleep(2)
                        st.rerun()
                
                with col_email:
                    if st.button("📧 M'envoyer ce brouillon", use_container_width=True):
                        import smtplib
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        try:
                            msg = MIMEMultipart("alternative")
                            msg["Subject"] = f"🤖 Brouillon I.A. de tournées - {date_planning.strftime('%d/%m/%Y')}"
                            msg["From"] = "smllivraisons@gmail.com"
                            msg["To"] = "smllivraisons@gmail.com"
                            
                            html_table = df_preview.to_html(index=False, border=1)
                            html_content = f"<h3>Proposition de tournées générée par l'IA pour le {date_planning.strftime('%d/%m/%Y')}</h3>{html_table}"
                            msg.attach(MIMEText(html_content, "html"))
                            
                            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                            # Using the App Password from your TOOLS.md notes
                            server.login("smllivraisons@gmail.com", "sncerbwvitfiqtjq")
                            server.sendmail("smllivraisons@gmail.com", "smllivraisons@gmail.com", msg.as_string())
                            server.quit()
                            st.success("✉️ Brouillon envoyé avec succès sur ta boîte mail !")
                        except Exception as e:
                            st.error(f"Erreur d'envoi : {e}")

                with col_cancel:
                    if st.button("❌ Refuser (Annuler)", use_container_width=True):
                        del st.session_state["ai_proposal"]
                        st.rerun()"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Email button injected.")
else:
    print("Old block not found.")
