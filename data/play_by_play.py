# -*- coding: utf-8 -*-
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def pg_array_format(lst):
    return '{' + ','.join(str(x) for x in lst) + '}'

def convert_minute_str(min_str):
    """Convertit MM:SS en minutes décimales, retourne None si erreur."""
    try:
        if isinstance(min_str, str) and ':' in min_str:
            mm, ss = min_str.split(':')
            return round(int(mm) + int(ss)/60, 2)
        elif pd.notna(min_str):
            return float(min_str)
    except:
        return None
    return None

def to_int(value):
    """Convertit proprement une valeur en int compatible base."""
    try:
        if value is None:
            return None
        f = float(value)
        return int(f)
    except:
        return None

def parse_player_name(full_name):
    try:
        name = str(full_name).strip()
        if name in ['Total', '-', '', 'player9']:
            return None, None
        parts = name.split()
        if len(parts) == 1:
            return parts[0], ""
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            name = ' '.join(parts[:-1])
            last_name = parts[-1]
            return name, last_name
    except:
        return str(full_name), ""

def normalize_name(name):
    return name.lower().replace('é', 'e').replace('è', 'e').replace('’', "'").replace('-', ' ').strip()

teams = supabase.table('team').select('id,name').execute()
players = supabase.table('player').select('id,name,last_name').execute()

team_name_to_id = {normalize_name(t['name']): t['id'] for t in teams.data}

player_map = {}
for p in players.data:
    prenom = normalize_name(p.get('name', ''))
    nom = normalize_name(p.get('last_name', ''))
    player_map[(prenom, nom)] = p['id']

file_path = r"C:\Users\guill\OneDrive\Documents\GitHub\BasketStatsAnalyzer\feuille_de_match\perso_play_by_playAubenas_vs_N3_OMMB_(2025-09-17_15_7).csv"
df = pd.read_csv(file_path, sep=';').head(20)

loc_cols = ['Joueur local 1', 'Joueur local 2', 'Joueur local 3', 'Joueur local 4', 'Joueur local 5']
vis_cols = ['Joueur visiteur 1', 'Joueur visiteur 2', 'Joueur visiteur 3', 'Joueur visiteur 4', 'Joueur visiteur 5']

def get_player_id_from_column(row, cols):
    ids = []
    for col in cols:
        player_name = row.get(col, '')
        prenom, nom = parse_player_name(player_name)
        prenom_n = normalize_name(prenom or '')
        nom_n = normalize_name(nom or '')
        pid = player_map.get((prenom_n, nom_n))
        if pid is not None:
            ids.append(pid)
    return ids


df['home_players_on_court'] = df.apply(lambda row: get_player_id_from_column(row, loc_cols), axis=1)
df['away_players_on_court'] = df.apply(lambda row: get_player_id_from_column(row, vis_cols), axis=1)


game_id = 2  # Assure-toi de définir ou récupérer ce game_id correctement

for idx, row in df.iterrows():
    equipe_raw = row.get('Équipe', '')
    equipe = normalize_name(equipe_raw)
    team_id = team_name_to_id.get(equipe)

    joueur_raw = row.get('Joueur', '')
    prenom, nom = parse_player_name(joueur_raw)
    prenom_n = normalize_name(prenom or '')
    nom_n = normalize_name(nom or '')

    player_id = player_map.get((prenom_n, nom_n))

    min_remaining = convert_minute_str(row.get('Minutes', None))
    home_score = to_int(row.get('Score local', None))
    away_score = to_int(row.get('Score visiteur', None))

    try:
        play_record = {
            'game_id': to_int(game_id),
            'period': to_int(row.get('Quart', None)),
            'min_remaining': min_remaining,
            'home_score': home_score,
            'away_score': away_score,
            'team_id': team_id,
            'player_1_id': player_id,
            'player_2_id': None,
            'type_off': row.get('Système offensif', None),
            'type_def': row.get('Système défensif', None),
            'play_type_1': row.get('Événement'),
            'description': row.get('Description',None),
            'points': 0,
            'is_made': None,
            'player_in_id': None,
            'player_out_id': None,
            'x': None,
            'y': None,
            # Conversion au format PostgreSQL array
            'home_players_on_court': pg_array_format(row.get('home_players_on_court', [])),
            'away_players_on_court': pg_array_format(row.get('away_players_on_court', [])),
        }
    except Exception as e:
        print(f"Erreur format données ligne {idx}: {e}")
        continue

    # Nettoyer NaN éventuels
    for k in play_record:
        if isinstance(play_record[k], float) and pd.isna(play_record[k]):
            play_record[k] = None

    response = supabase.table('play_by_play').insert(play_record).execute()
    if getattr(response, 'status_code', None) == 201:
        print(f"Insertion OK ligne {idx}")
    else:
        print(f"Échec insertion ligne {idx}: {getattr(response, 'error', response)}")

print("Traitement terminé.")
