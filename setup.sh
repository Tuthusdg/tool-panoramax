#!/bin/bash

# Crée un environnement virtuel sur le bureau
python3 -m venv ~/Desktop/tool-panoramax

# Active l’environnement virtuel
source ~/Desktop/tool-panoramax/bin/activate

# Installe les dépendances nécessaires
pip install --upgrade pip
pip install pillow gpsphoto geopandas pandas
