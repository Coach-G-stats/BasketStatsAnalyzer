# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv



# Charger variables d'environnement Supabase
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

st.title("Insertion statistiques basketball")

uploaded_file = st.file_uploader("Glisse ton fichier stats CSV ici", type=["csv"])

season = st.text_input("Saison (ex: 2025-2026)")
phase = st.text_input("Phase (ex: regular season)")
game_date = st.date_input("Date du match")
home_score = st.number_input("Score domicile", min_value=0)
away_score = st.number_input("Score extérieur", min_value=0)

if st.button("Insérer les données") and uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # Appeler ici tes fonctions avec df et les infos ci-dessus
    st.success("Insertion terminée avec succès !")

