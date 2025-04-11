import pandas as pd
import random
import json
import os

# Étape de vérification avant exécution
def pre_execution_questions():
    """
    Pose des questions à l'utilisateur pour vérifier certains points avant l'exécution du code principal.
    """
    print("Avant de commencer, vérifiez les points suivants :")
    
    # Liste de questions à poser
    questions = [
        "L'appel a-t-il été fait sur la feuille correspondante (Classeur_étudiants.xlsx) ? (oui/non) ",
        "La bonne semaine est-elle renseignée dans le code ? (oui/non) ",
    ]

    # Vérifier les réponses
    for question in questions:
        response = input(question).strip().lower()
        while response not in ["oui", "non"]:
            print("Veuillez répondre par 'oui' ou 'non'.")
            response = input(question).strip().lower()
        if response == "non":
            print("Veuillez corriger ce point avant de lancer le script.")
            exit("Exécution interrompue par l'utilisateur.")  # Stoppe l'exécution si une réponse est 'non'

    print("Vérifications terminées. Le script va maintenant s'exécuter.")


pre_execution_questions()


def load_students_from_excel(file_path, sheet_name, already_selected=None, presence_column="SEMAINE 4"):
    """
    Charge les étudiants d'une feuille spécifique dans un fichier Excel, sélectionne un tiers
    aléatoire d'étudiants sans répétition et en prenant en compte leur présence.

    Args:
        file_path (str): Chemin du fichier Excel.
        sheet_name (str): Nom de la feuille à traiter.
        already_selected (set): Ensemble des étudiants déjà sélectionnés.
        presence_column (str): Nom de la colonne indiquant la présence.

    Returns:
        list: Liste des étudiants sélectionnés.
        set: Ensemble mis à jour des étudiants déjà sélectionnés.
    """
    if already_selected is None:
        already_selected = set()

    # Charger la feuille spécifique
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Vérifier que les colonnes nécessaires existent
    required_columns = ["NOM", "PRÉNOM", presence_column]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"La feuille {sheet_name} doit contenir les colonnes {required_columns}.")
    
    # Combiner NOM et PRÉNOM pour former une identité unique
    df['IDENTITÉ'] = df['PRÉNOM'] + ' ' + df['NOM']
    
    # Filtrer les étudiants éligibles : présents et non encore sélectionnés
    eligible_students = df[
        (df[presence_column] == "Présent") & 
        (~df['IDENTITÉ'].isin(already_selected))
    ]
    
    # Calculer un tiers des étudiants éligibles
    num_to_select = max(1, len(df[df[presence_column] == "Présent"]) // 3)  # Au moins 1 étudiant si possible
    
    # Sélectionner aléatoirement un tiers des étudiants
    if num_to_select > 0:
        selected_students = eligible_students.sample(n=num_to_select, random_state=random.randint(1, 1000))
        
        # Ajouter les étudiants sélectionnés à l'ensemble
        already_selected.update(selected_students['IDENTITÉ'])
        
        # Retourner la liste des étudiants sélectionnés
        return selected_students['IDENTITÉ'].tolist(), already_selected
    else:
        return [], already_selected


def load_history(history_file):
    """
    Charge l'historique des étudiants sélectionnés depuis un fichier JSON.

    Args:
        history_file (str): Chemin du fichier d'historique.

    Returns:
        set: Ensemble des étudiants déjà sélectionnés.
    """
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            return set(json.load(file))  # Charger et convertir en ensemble
    return set()


def save_history(history, history_file):
    """
    Sauvegarde l'historique des étudiants sélectionnés dans un fichier JSON.

    Args:
        history (set): Ensemble des étudiants sélectionnés.
        history_file (str): Chemin du fichier d'historique.
    """
    with open(history_file, "w") as file:
        json.dump(list(history), file)  # Convertir en liste pour JSON


# Charger les données des étudiants
excel_file = "Classeur_étudiants.xlsx"  # Remplacez par le chemin de votre fichier Excel
presence_column = "SEMAINE 4"  # Nom de la colonne indiquant la présence
history_file = "historique_exam_G04.json"  # Fichier pour sauvegarder l'historique

# Charger l'historique des étudiants sélectionnés
already_selected_students = load_history(history_file)

# Spécifiez la feuille à traiter
sheet_name = "G04"

# Sélectionner les étudiants pour la feuille choisie
try:
    selected_students, already_selected_students = load_students_from_excel(
        excel_file, sheet_name, already_selected_students, presence_column
    )

    # Sauvegarder l'historique mis à jour
    save_history(already_selected_students, history_file)

    # Afficher les résultats
    print(f"Étudiants sélectionnés pour la feuille {sheet_name} : {selected_students}")

except ValueError as e:
    print("Erreur :", e)
except FileNotFoundError:
    print(f"Erreur : Le fichier Excel {excel_file} est introuvable.")