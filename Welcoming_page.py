import streamlit as st

# Set the title of the page
st.set_page_config(page_title="Welcome Page", page_icon="👋")

# Welcome message
st.title("Bienvenue sur l'application *Arpenter à l'université* 👋")
st.subheader("Je suis très heureux de vous compter parmi nous.")

# Add some description
st.write("""
Cette application a été conçue pour vous aider à gérer vos groupes de lecture de manière efficace et amusante dans le
         cadre du développement des méthodes pédagogiques ayant recours à *l'arpentage* en milieu universitaire. Ses fonctionnalités
         vous permettront de générer des groupes de lecture de façon aléatoire, mais aussi de sélectionner des élèves
         au hasard pour évaluer leurs travaux.
""")

st.sidebar.success("Select Any Page from here") 

# Add creator's name at the bottom of the page
st.markdown("---")
st.markdown("*Créé par Pablo Aubert-Lacombe, membre du Centre Maurice Halbwachs et chercheur associé à l'École d'économie de Paris*")