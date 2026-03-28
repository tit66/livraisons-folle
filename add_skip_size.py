import re

with open("app.py", "r") as f:
    content = f.read()

old_settings_block = """                            for s, c in new_counts.items():
                                run_query("UPDATE skip_inventory SET total_count = :c WHERE size = :s", {"c": c, "s": s})
                            st.success("✅ Stock global mis à jour avec succès !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")"""

new_settings_block = """                            for s, c in new_counts.items():
                                run_query("UPDATE skip_inventory SET total_count = :c WHERE size = :s", {"c": c, "s": s})
                            st.success("✅ Stock global mis à jour avec succès !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                            
                st.divider()
                st.write("### ➕ Ajouter un nouveau volume de benne")
                with st.form("add_size_form"):
                    col_ns1, col_ns2 = st.columns(2)
                    with col_ns1:
                        new_size_name = st.text_input("Nouveau volume (Ex: 12m3)")
                    with col_ns2:
                        new_size_qty = st.number_input("Quantité possédée", min_value=0, value=0, step=1)
                    if st.form_submit_button("✅ Ajouter le nouveau volume", type="primary"):
                        if new_size_name:
                            try:
                                run_query("INSERT INTO skip_inventory (size, total_count) VALUES (:s, :c)", {"s": new_size_name, "c": new_size_qty})
                                st.success(f"Volume {new_size_name} ajouté !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur (le volume existe peut-être déjà) : {e}")
                        else:
                            st.error("Le nom du volume est obligatoire.")"""

if old_settings_block in content:
    content = content.replace(old_settings_block, new_settings_block)
    print("Settings block updated.")
else:
    print("Could not find the settings block.")

with open("app.py", "w") as f:
    f.write(content)

