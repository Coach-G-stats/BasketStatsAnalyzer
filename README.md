# BasketStatsAnalyzer
Outil d'analyse de stats pour une équipe de Nationale 3 – Stats basiques/avancées et dashboards interactifs

## Description
Outil personnel d'analyse de données pour une équipe de basket en Nationale 3. Ce projet permet de collecter, stocker et analyser des statistiques basiques (points, rebonds, assists) et avancées (PER, TS%, etc.). Il inclut des tableaux de bord interactifs pour visualiser les performances.

### Objectifs
- Centraliser et analyser les données de matchs, rosters, joueurs et actions dans une base robuste
- Automatiser l’extraction des stats depuis CSV et feuilles de match PDF
- Générer des dashboards interactifs pour visualiser et explorer les performances
- Calculer des statistiques avancées : points sur rebond offensif, paniers rapides (<8 sec), paniers avec la faute, etc.
- Structurer un workflow ETL modulaire (Python/SQL/Airflow/dbt envisageables)

### Technologies utilisées
- Collecter des données via SQL (stockage sur Supabase).
- Traiter les stats avec Python (pandas, numpy).
- Créer des dashboards interactifs avec Streamlit.
- Déployer l'outil en ligne (Heroku ou similaire).
- GitHub pour le versionning

###  Fonctionnalités
- Import automatisé de fichiers CSV/PDF via Python
- Extraction d’identifiants, mapping des joueurs avec gestion des prénoms/français spécifiques
- Insertion automatisée dans Supabase/Postgres avec gestion des contraintes
- Tableaux de bord Streamlit pour l’analyse des matchs et joueurs
- Vues/tables de statistiques avancées
- Exemple d’API Postgres via Supabase pour queries et gestion des données

### Comment lancer le projet localement

### Auteur
Guillaume Allias – Analyste Data & Basket. Contact : https://www.linkedin.com/in/guillaume-allias/


