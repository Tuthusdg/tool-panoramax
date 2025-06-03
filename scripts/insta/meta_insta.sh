#!/bin/bash

# Dossier contenant les images
DOSSIER="$1"

# Résolution cible
WIDTH=3840
HEIGHT=1920

# Récupérer la liste des images
IMAGES=("$DOSSIER"/*.jpg)
TOTAL=${#IMAGES[@]}
COMPTEUR=0

# Fonction pour afficher une barre de progression
progress_bar() {
  local progress=$1
  local total=$2
  local percent=$(( progress * 100 / total ))
  local filled=$(( percent / 2 ))
  local empty=$(( 50 - filled ))
  printf "\rTraitement : ["
  printf "%0.s█" $(seq 1 $filled)
  printf "%0.s " $(seq 1 $empty)
  printf "] %d%% (%d/%d)" "$percent" "$progress" "$total"
}

# Parcours des fichiers .jpg dans le dossier
for f in "${IMAGES[@]}"; do
    ((COMPTEUR++))
    progress_bar "$COMPTEUR" "$TOTAL"

    # Application des métadonnées avec exiftool
    exiftool -overwrite_original \
        -ProjectionType="equirectangular" \
        -UsePanoramaViewer=True \
        -CroppedAreaImageWidthPixels=$WIDTH \
        -CroppedAreaImageHeightPixels=$HEIGHT \
        -FullPanoWidthPixels=$WIDTH \
        -FullPanoHeightPixels=$HEIGHT \
        -CroppedAreaLeftPixels=0 \
        -CroppedAreaTopPixels=0 \
        -PoseHeadingDegrees=0 \
        "$f" > /dev/null 2>&1
done

# Saut de ligne final
echo -e "\n✅ Traitement terminé."
