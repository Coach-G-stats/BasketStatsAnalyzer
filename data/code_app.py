# -*- coding: utf-8 -*-

from dotenv import load_dotenv
import os
from supabase import create_client
import pandas as pd

# Charger votre fichier .env
load_dotenv()

# Se connecter avec vos variables d'environnement
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Lire une table (remplacez "team" par le nom réel)
response = supabase.table("team").select("*").execute()
df = pd.DataFrame(response.data)

print(f"✅ {len(df)} lignes récupérées")
print(df.head())

