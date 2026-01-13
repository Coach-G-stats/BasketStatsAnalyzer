# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from integration_data import (
    create_teams,
    create_roster_from_boxscore_split,
    create_game,
    insert_game_stats
)
# from play_by_play import insert_play_by_play  # Ajoute si besoin pour Play-by-Play

st.title("Importer des statistiques (Box Score ou Play-by-Play)")

data_type = st.radio("Quel type de fichier ?", ("Box Score", "Play-by-Play"))

uploaded_file = st.file_uploader("Dépose ton fichier CSV", type=["csv"])

season = st.text_input("Saison", "2025-2026")
phase = st.text_input("Phase (ex: regular season)", "regular season")
game_date = st.date_input("Date du match")
home_score = st.number_input("Score domicile", min_value=0)
away_score = st.number_input("Score extérieur", min_value=0)
home_team = st.text_input("Nom équipe domicile")
away_team = st.text_input("Nom équipe extérieur")

if st.button("Insérer les données") and uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # 1. Création ou récupération des équipes
        team_ids = {}
        for team_name in [home_team, away_team]:
            tid_dict = create_teams([{"name": team_name, "city": ""}])  # Doit retourner un dict nom: id
            team_ids[team_name] = tid_dict[team_name]

        # 2. Création/maj des rosters (optionnel pour play-by-play selon ton modèle)
        if data_type == "Box Score":
            create_roster_from_boxscore_split(df, team_ids[home_team], season, 1)
            create_roster_from_boxscore_split(df, team_ids[away_team], season, 2)

        # 3. Création du match (dans Supabase)
        game_data = {
            "game_date": str(game_date),
            "season": season,
            "phase": phase,
            "home_roster_id": team_ids[home_team],   # Vérifie bien ces champs selon ton modèle
            "away_roster_id": team_ids[away_team],
            "home_score": home_score,
            "away_score": away_score,
            "winner": team_ids[home_team] if home_score > away_score else team_ids[away_team],
            "overtime": False,
            "location": ""  # Ajoute un champ si tu veux
        }
        game_id = create_game(game_data)   # Doit retourner l'id du match inséré

        # 4. Insertion des stats
        if data_type == "Box Score":
            insert_game_stats(game_id, df)
            st.success("Box Score inséré et match créé dans Supabase !")
        elif data_type == "Play-by-Play":
            # insert_play_by_play(game_id, df)   # Décommente quand tu l'auras codé/importé
            st.success("Play-by-Play inséré et match créé dans Supabase !")

    except Exception as e:
        st.error(f"Erreur lors de l'insertion : {e}")
