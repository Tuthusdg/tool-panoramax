#!/bin/bash

# Si le script est appelé sans source, avertir et quitter
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ Ce script doit être exécuté avec 'source ./setup.sh' pour que l'environnement reste actif."
    exit 1
fi

# Fonction utilitaire pour afficher une étape avec statut
step() {
    echo -ne "[ ] $1...\r"
}

step_done() {
    echo -e "[✔] $1"
}

# Étape 1 : Créer un environnement virtuel
step "Création de l'environnement virtuel"
python3 -m venv ~/Desktop/tool-panoramax > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[✘] Erreur lors de la création de l'environnement virtuel"
    return 1
fi
step_done "Environnement virtuel créé"

# Étape 2 : Activation de l'environnement
step "Activation de l'environnement"
source ~/Desktop/tool-panoramax/bin/activate
step_done "Environnement activé"

# Étape 3 : Mise à jour de pip
step "Mise à jour de pip"
pip install --upgrade pip > /dev/null 2>&1
step_done "pip mis à jour"

# Étape 4 : Installation des paquets
PACKAGES=("pillow" "gpsphoto" "geopandas" "pandas" "exifread" "piexif" "tqdm")

for pkg in "${PACKAGES[@]}"; do
    step "Installation de $pkg"
    pip install "$pkg" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[✘] Échec de l'installation de $pkg"
        return 1
    fi
    step_done "$pkg installé"
done
mkdir kml_here
mkdir img_to_be_changed
echo -e "\n✅ Installation terminée avec succès. L’environnement est actif."
