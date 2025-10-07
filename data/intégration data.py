# -*- coding: utf-8 -*-

"""
INTÉGRATION FINALE CSV -> SUPABASE
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime
import numpy as np

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
    
"""Crée les équipes"""
def create_teams():
    
    print("Gestion des équipes...")
    
    teams = [
        {"name": "Aubenas", "city": "Aubenas"},
        {"name": "N3 OMMB", "city": "Montpellier"}
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