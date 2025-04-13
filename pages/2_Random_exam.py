import streamlit as st
import pandas as pd
import random
import json
import os

# Constantes
excel_file = "Classeur_étudiants.xlsx"
history_file = "historique_exam.json"

# Fonctions
def get_sheet_names(excel_path):
    return pd.ExcelFile(excel_path).sheet_names

def load_students_from_excel(file_path, sheet_name, already_selected=None, presence_column=None):
    if already_selected is None:
        already_selected = set()

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    required_columns = ["NOM", "PRÉNOM", presence_column]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"La feuille {sheet_name} doit contenir les colonnes {required_columns}.")
    
    df['IDENTITÉ'] = df['PRÉNOM'] + ' ' + df['NOM']
    eligible_students = df[
        (df[presence_column] == "Présent") & 
        (~df['IDENTITÉ'].isin(already_selected))
    ]
    num_to_select = max(1, len(df[df[presence_column] == "Présent"]) // 3)

    if num_to_select > 0 and not eligible_students.empty:
        selected_students = eligible_students.sample(n=min(num_to_select, len(eligible_students)), random_state=random.randint(1, 1000))
        already_selected.update(selected_students['IDENTITÉ'])
        return selected_students['IDENTITÉ'].tolist(), already_selected
    else:
        return [], already_selected

def load_history(history_file):
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_history(history, history_file):
    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

# Interface Streamlit
st.set_page_config(page_title="Sélection d'étudiants", page_icon="🎓", layout="wide")
st.title("🎓 Sélection aléatoire d'étudiants présents")

# --- Gestion de l'état de validation ---
if "verif_ok" not in st.session_state:
    st.session_state.verif_ok = False

# === Étape 1 : Vérifications préalables ===
st.subheader("🧐 Étape 1 : Vérifications")
q1 = st.radio("L'appel a-t-il été fait sur la feuille Excel et le document a-t-il été enregistré ?", ["Oui", "Non"])

if st.button("✅ Valider les vérifications"):
    if q1 == "Oui":
        st.session_state.verif_ok = True
        st.success("✅ Vérifications validées. Vous pouvez continuer.")
    else:
        st.warning("Veuillez répondre 'Oui' pour continuer.")

# === Suite uniquement si validation ok ===
if st.session_state.verif_ok:

    # Étape 2 : Choix de la feuille
    st.subheader("📄 Étape 2 : Choix de la feuille Excel")
    sheets = get_sheet_names(excel_file)
    sheet_name = st.selectbox("Sélectionnez une feuille Excel :", sheets)

    # Étape 3 : Choix de la semaine
    st.subheader("🗓️ Étape 3 : Choix de la semaine")
    df_preview = pd.read_excel(excel_file, sheet_name=sheet_name)
    columns_pres = [col for col in df_preview.columns if col.startswith("SEMAINE")]
    presence_column = st.selectbox("Choisissez la colonne de présence (semaine) :", columns_pres)

    # Étape 4 : Sélection
    st.subheader("🎯 Étape 4 : Sélection")
    if st.button("🎲 Lancer la sélection aléatoire d'étudiants"):
        try:
            raw_history = load_history(history_file)
            already_selected = {entry["Identité"] for entry in raw_history if entry["Feuille"] == sheet_name}

            selected, updated_set = load_students_from_excel(
                excel_file, sheet_name, already_selected, presence_column
            )

            if selected:
                # Mise à jour de l'historique complet
                for identity in selected:
                    raw_history.append({"Identité": identity, "Feuille": sheet_name})
                save_history(raw_history, history_file)

                # Infos de sélection
                total_presents = df_preview[df_preview[presence_column] == "Présent"].shape[0]
                num_to_select = max(1, total_presents // 3)

                st.success("🎉 Étudiants sélectionnés avec succès !")
                st.markdown(f"**📊 {total_presents} étudiant·es présent·es** dans la feuille **{sheet_name}**.")
                st.markdown(f"**🔢 Sélection d’un tiers : {num_to_select} étudiant·es choisi·es** au hasard.")
                st.table(pd.DataFrame(selected, columns=["Identité"]))

            else:
                st.warning("Aucun étudiant éligible ou tous déjà sélectionnés.")

        except Exception as e:
            st.error(f"Erreur lors de l'exécution : {str(e)}")

    # Historique
    if st.checkbox("📜 Afficher l'historique complet"):
        raw_history = load_history(history_file)
        if raw_history:
            df_hist = pd.DataFrame(raw_history)
            st.table(df_hist.sort_values(by="Feuille"))
        else:
            st.info("Aucun étudiant sélectionné pour le moment.")

    # Option : reset vérification
    if st.button("🔄 Recommencer les vérifications"):
        st.session_state.verif_ok = False
        st.experimental_rerun()
