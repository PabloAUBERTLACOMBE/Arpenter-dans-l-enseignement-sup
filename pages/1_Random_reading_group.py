import pandas as pd
import json
import os
import random
import streamlit as st



# Paramètres
excel_file = "Classeur_étudiants.xlsx"
history_base_file = "group_history_"

# Fonctions
def get_sheet_names(file_path):
    xls = pd.ExcelFile(file_path)
    return xls.sheet_names

def load_students_from_excel(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    if "NOM" not in df.columns or "PRÉNOM" not in df.columns:
        raise ValueError("Le fichier Excel doit contenir les colonnes 'NOM' et 'PRÉNOM'.")
    return [f"{prenom} {nom}" for prenom, nom in zip(df["PRÉNOM"], df["NOM"])]

def load_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def generate_groups(students, num_groups, history, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        random.shuffle(students)
        groups = [students[i::num_groups] for i in range(num_groups)]
        if not any(groups == past for past in history):
            history.append(groups)
            return groups, history
    raise RuntimeError("Impossible de générer des groupes uniques après plusieurs essais.")

# --- UI Streamlit ---

st.set_page_config(layout="wide")

st.title("🎲 Générateur aléatoire de groupes de lecture")

# Sélection de la feuille
sheets = get_sheet_names(excel_file)
sheet_name = st.selectbox("Sélectionnez une feuille Excel :", sheets)

# Nombre de groupes
num_groups = st.number_input("Nombre de groupes", min_value=2, max_value=20, value=6, step=1)

# Option de réinitialisation
reset_history = st.checkbox("Réinitialiser l'historique des groupes")

# Bouton pour lancer la génération
if st.button("Générer les groupes"):
    with st.spinner("⏳ Génération des groupes en cours..."):
        try:
            students = load_students_from_excel(excel_file, sheet_name)
            history_file = f"{history_base_file}{sheet_name}.json"
            
            # Gérer l’historique
            history = [] if reset_history else load_history(history_file)
            groups, updated_history = generate_groups(students, num_groups, history)
            save_history(updated_history, history_file)

            # Construire et afficher la table
            group_data = []
            for i, group in enumerate(groups, 1):
                rapporteur = group[0] if group else "Aucun"
                group_data.append({
                    "Groupe": f"Groupe {i}",
                    "Membres": ", ".join(group),
                    "Rapporteur·rice": rapporteur
                })

            df_groups = pd.DataFrame(group_data)
            st.success("✅ Groupes générés avec succès !")
            st.table(df_groups)

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

# Bouton pour afficher l'historique
if st.button("Afficher l'historique des groupes"):
    try:
        history_file = f"{history_base_file}{sheet_name}.json"
        history = load_history(history_file)

        if not history:
            st.info("ℹ️ Aucun historique trouvé pour cette feuille.")
        else:
            st.subheader("📜 Historique des groupes générés")
            for idx, past_groups in enumerate(history, start=1):
                st.markdown(f"**Tirage #{idx}**")
                for i, group in enumerate(past_groups, start=1):
                    rapporteur = group[0] if group else "Aucun"
                    st.markdown(f"- **Groupe {i}** : {', '.join(group)}  _(Rapporteur·rice : {rapporteur})_")
                st.markdown("---")

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de l’historique : {str(e)}")
