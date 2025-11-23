# -*- coding: utf-8 -*-

"""
INTÉGRATION FINALE CSV -> SUPABASE
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import numpy as np

# Charger votre fichier .env
load_dotenv()

# Se connecter avec variables d'environnement
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("INTÉGRATION CSV FINALE - BASKET DASHBOARD")
print("=" * 55)

    
"""Parse 'Prénom NOM' ou 'Prénom-Composé NOM'"""   
def parse_player_name(full_name):
    try:
        # Nettoyer le nom
        name = str(full_name).strip()
        
        # Cas spéciaux
        if name in ['Total', '-', '', 'player9']:
            return None, None
            
        # Séparer par espace
        parts = name.split()
        
        if len(parts) == 1:
            # Un seul mot = prénom seul
            return parts[0], ""
        elif len(parts) == 2:
            # Deux mots = "Prénom NOM"
            return parts[0], parts[1]
        else:
            # Plus de deux mots = "Prénom1-Prénom2 NOM" ou "Prénom NOM DE FAMILLE"
            # Dernier mot = nom de famille, le reste = prénom
            first_name = ' '.join(parts[:-1])
            last_name = parts[-1]
            return first_name, last_name
            
    except:
        return str(full_name), ""
    
"""convertie % en numérique"""   
    
def convert_percent_str(percent_str):
    try:
        if isinstance(percent_str, str) and percent_str.endswith('%'):
            return round(float(percent_str[:-1]) / 100, 4)
        elif pd.notna(percent_str):
            return float(percent_str)
    except:
        return None
    return None
    

"""convertie format minutes'"""   

def convert_minute_str(min_str):
    try:
        if isinstance(min_str, str) and ':' in min_str:
            mm, ss = min_str.split(':')
            return round(int(mm) + int(ss)/60, 2)  # minutes décimales ex 13.28
        elif pd.notna(min_str):
            return float(min_str)
    except:
        return None
    return None
    
"""Crée les équipes"""
def create_teams():
    
    print("Gestion des équipes...")
    
    teams = [
        {"name": "USAB", "city": "Aubenas"},
        {"name": "OMMB", "city": "Saint-Jaen de Védas"}
    ]
    
    team_ids = {}
    
    for team in teams:
        try:
            # Vérifier si l'équipe existe
            result = supabase.table('team').select('id').eq('name', team['name']).execute()
            
            if result.data:
                team_id = result.data[0]['id']
                print(f"✅ Équipe {team['name']} existe (ID: {team_id})")
            else:
                # Créer l'équipe
                result = supabase.table('team').insert(team).execute()
                team_id = result.data[0]['id']
                print(f"✅ Équipe {team['name']} créée (ID: {team_id})")
            
            team_ids[team['name']] = team_id
            
        except Exception as e:
            print(f"❌ Erreur équipe {team['name']}: {e}")
    
    return team_ids
if __name__ == "__main__":
    create_teams()
    
print("Création du match...")
    
def create_game(team_ids):  
    game_data = {
        'game_date': '2025-09-13',  # à personnaliser
        'season': '2025-2026',
        'phase': 'regular season',
        'home_roster_id': team_ids.get('USAB'),
        'away_roster_id': team_ids.get('OMMB'),
        'home_score': 85,
        'away_score': 76,
        'winner': team_ids.get('USAB'),
        'overtime': False,
        'location': 'Aubenas Gym'
    }
    try:
        result = supabase.table('game').insert(game_data).execute()
        game_id = result.data[0]['id']
        print(f"✅ Match créé, game_id={game_id}")
        return game_id
    except Exception as e:
        print(f"❌ Erreur création match: {e}")
        return None



def get_or_create_player(first_name, last_name):
    try:
        result = supabase.table('player').select('id').eq('name', first_name).eq('last_name', last_name).execute()
        if result.data:
            return result.data[0]['id']
        else:
            insert = supabase.table('player').insert({'name': first_name, 'last_name': last_name}).execute()
            return insert.data[0]['id']
    except Exception as e:
        print(f"❌ Erreur joueur {first_name} {last_name}: {e}")
        return None

def create_roster_from_boxscore_split(csv_path, team_id, season, team_number):
    df = pd.read_csv(csv_path)
    
    # Trouver l'index des lignes "Total" qui séparent les équipes
    total_indices = df.index[df['Joueur'] == 'Total'].tolist()
    if len(total_indices) < 2:
        print("Erreur: le fichier ne semble pas contenir deux sections équipes bien distinctes")
        return
    
    # Définir les bornes de section selon équipe (1 ou 2)
    if team_number == 1:
        df_team = df.loc[:total_indices[0]-1]
    else:
        df_team = df.loc[total_indices[0]+1:total_indices[1]-1]
    
    for _, row in df_team.iterrows():
        if 'Nº' not in row or pd.isna(row['Nº']):
            print(f"Ligne rejetée (pas de numéro): {row.to_dict()}")
            continue
        jersey_number = row['Nº']
        full_name = row['Joueur'] if 'Joueur' in row else None
        if pd.isna(full_name) or full_name in ['Total', '-', 'player9']:
            continue
        first, last = parse_player_name(full_name)
        if not first:
            continue
        player_id = get_or_create_player(first, last)
        # Vérifier doublon avant insertion
        ex = supabase.table('roster').select('id').eq('team_id', team_id).eq('player_id', player_id).eq('season', season).execute()
        if not ex.data:
            rec = {
                'team_id': team_id,
                'player_id': player_id,
                'jersey_number': int(jersey_number),
                'season': season
            }
            supabase.table('roster').insert(rec).execute()
            print(f"Insertion {rec}")
        else:
            print(f"Déjà dans le roster: {first} {last}")

# Utilisation
if __name__ == "__main__":
    team_ids = create_teams()  # ta fonction existante
    create_roster_from_boxscore_split(
        r"C:\Users\guill\OneDrive\Documents\GitHub\BasketStatsAnalyzer\feuille_de_match\box_score_stats-aubenas-vs-n3_ommb-18-09-2025.csv",
        team_ids['USAB'],
        '2025-2026',
        1  # équipe 1 dans le csv
    )
    create_roster_from_boxscore_split(
        r"C:\Users\guill\OneDrive\Documents\GitHub\BasketStatsAnalyzer\feuille_de_match\box_score_stats-aubenas-vs-n3_ommb-18-09-2025.csv",
        team_ids['OMMB'],
        '2025-2026',
        2  # équipe 2 dans le csv
    )



def insert_game_stats(game_id, stats_df):
    print("Insertion des statistiques joueurs…")
    for _, row in stats_df.iterrows():
        first_name, last_name = parse_player_name(row['Joueur'])
        if first_name is None:
            continue  # Skip les totaux ou lignes vides
        player_id = get_or_create_player(first_name, last_name)
        if player_id is None:
            continue
        minutes = convert_minute_str(row.get('MIN', None))
        # Exclure les joueurs à 0 minute
        if minutes is None or minutes == 0:
            continue

        stat_data = {
    'game_id': game_id,
    'player_id': player_id,
    'jersey_number': int(row.get('Nº', 0)) if pd.notna(row.get('Nº')) else None,
    'min': convert_minute_str(row.get('MIN', None)),
    'pts': int(row.get('PTS', 0)) if pd.notna(row.get('PTS')) else 0,
    'fg': int(row.get('TR', 0)) if pd.notna(row.get('TR')) else 0,
    'fga': int(row.get('TT', 0)) if pd.notna(row.get('TT')) else 0,
    'fg%': convert_percent_str(row.get('%TIRS', None)),
    '3p': int(row.get('3R', 0)) if pd.notna(row.get('3R')) else 0,
    '3pa': int(row.get('3T', 0)) if pd.notna(row.get('3T')) else 0,
    '3p%': convert_percent_str(row.get('%3', None)),
    '2p': int(row.get('2R', 0)) if pd.notna(row.get('2R')) else 0,
    '2pa': int(row.get('2T', 0)) if pd.notna(row.get('2T')) else 0,
    '2p%': convert_percent_str(row.get('%2', None)),
    'ft': int(row.get('LFR', 0)) if pd.notna(row.get('LFR')) else 0,
    'fta': int(row.get('LFT', 0)) if pd.notna(row.get('LFT')) else 0,
    'ft%': convert_percent_str(row.get('%LF', None)),
    'oreb': int(row.get('REBO', 0)) if pd.notna(row.get('REBO')) else 0,
    'dreb': int(row.get('REBD', 0)) if pd.notna(row.get('REBD')) else 0,
    'reb': int(row.get('REB', 0)) if pd.notna(row.get('REB')) else 0,
    'ast': int(row.get('PD', 0)) if pd.notna(row.get('PD')) else 0,
    'tov': int(row.get('BP', 0)) if pd.notna(row.get('BP')) else 0,
    'stl': int(row.get('IN', 0)) if pd.notna(row.get('IN')) else 0,
    'blk': int(row.get('CT', 0)) if pd.notna(row.get('CT')) else 0,
    'sr': int(row.get('SR', 0)) if pd.notna(row.get('SR')) else 0,
    'pf': int(row.get('FP', 0)) if pd.notna(row.get('FP')) else 0,
    'fd': int(row.get('FPP', 0)) if pd.notna(row.get('FPP')) else 0,
    'pir': int(row.get('PIR', 0)) if pd.notna(row.get('PIR')) else 0,
    'eva': int(row.get('EVA', 0)) if pd.notna(row.get('EVA')) else 0,
    '+/-': int(row.get('+/-', 0)) if pd.notna(row.get('+/-')) else 0,
}

        try:
            supabase.table('game_stats').insert(stat_data).execute()
            print(f"✅ Stats insérées {first_name} {last_name}")
        except Exception as e:
            print(f"❌ Erreur insertion stats joueur {first_name} {last_name}: {e}")

if __name__ == "__main__":
    team_ids = create_teams()
    game_id = create_game(team_ids)
    if game_id:
        # Affiche le chemin de ton vrai fichier CSV
        csv_file = r'C:\Users\guill\OneDrive\Documents\GitHub\BasketStatsAnalyzer\feuille_de_match\box_score_stats-aubenas-vs-n3_ommb-18-09-2025.csv'
        stats_df = pd.read_csv(csv_file)
        insert_game_stats(game_id, stats_df)
        print("✔️ Insertion des stats joueurs terminée")
    else:
        print("⚠️ Pas de game_id, insertion stats impossible")
