import re

with open("app.py", "r") as f:
    content = f.read()

old_block = """                            except Exception as e:
                                st.error(f"Erreur (le volume existe peut-être déjà) : {e}")
                        else:
                            st.error("Le nom du volume est obligatoire.")"""

new_block = """                            except Exception as e:
                                st.error(f"Erreur (le volume existe peut-être déjà) : {e}")
                        else:
                            st.error("Le nom du volume est obligatoire.")
                            
                st.divider()
                st.write("### 🗑️ Supprimer un volume de benne")
                with st.form("delete_size_form"):
                    size_to_delete = st.selectbox("Volume à supprimer :", options=df_inv["Volume de la Benne"].tolist() if not df_inv.empty else [])
                    st.warning("⚠️ Attention, cela supprimera ce volume de l'inventaire et des choix de commandes.")
                    if st.form_submit_button("❌ Supprimer définitivement"):
                        if size_to_delete:
                            try:
                                run_query("DELETE FROM skip_inventory WHERE size = :s", {"s": size_to_delete})
                                st.success(f"Volume {size_to_delete} supprimé avec succès !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur lors de la suppression : {e}")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Delete block added successfully.")
else:
    print("Could not find the target block to append to.")

with open("app.py", "w") as f:
    f.write(content)

