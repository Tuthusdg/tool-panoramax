#!/bin/bash

SRC_DIR="$1"
OUT_DIR="img_logo"
LOGO_PATH="logo.png"

mkdir -p "$OUT_DIR"

if [ ! -f "$LOGO_PATH" ]; then
  echo "❌ Le fichier logo.png est introuvable."
  exit 1
fi

# Récupérer toutes les images .jpg
images=("$SRC_DIR"/*.jpg)
total=${#images[@]}
current=0

# Fonction pour afficher la barre de progression
progress_bar() {
  local progress=$1
  local total=$2
  local percent=$(( progress * 100 / total ))
  local filled=$(( percent / 2 ))
  local empty=$(( 50 - filled ))
  printf "\rProgression : ["
  printf "%0.s█" $(seq 1 $filled)
  printf "%0.s " $(seq 1 $empty)
  printf "] %d%% (%d/%d)" "$percent" "$progress" "$total"
}

for img in "${images[@]}"; do
  ((current++))
  progress_bar "$current" "$total"

  # Vérification que le fichier est valide
  if [ ! -f "$img" ] || [ ! -s "$img" ]; then
    continue
  fi

  filename=$(basename "$img")
  output="$OUT_DIR/$filename"

  # Lire les dimensions de l'image
  dimensions=$(identify -format "%wx%h" "$img" 2>/dev/null)
  largeur=$(echo "$dimensions" | cut -d'x' -f1)
  hauteur=$(echo "$dimensions" | cut -d'x' -f2)

  # Vérifier le ratio 2:1
  if [ $((largeur / hauteur)) -ne 2 ]; then
    continue
  fi

  nadir_height=$((hauteur / 10))
  nadir_offset=$((hauteur - nadir_height))

  # Lire le sampling factor
  sampling=$(identify -verbose "$img" | grep -i "sampling factor" | head -n1 | awk -F ':' '{print $2}' | tr -d ' ')
  sampling=${sampling:-2x2}

  # Générer le nadir
  convert "$LOGO_PATH" -rotate 180 -distort DePolar 0 -flip -flop \
    -geometry "${largeur}x${nadir_height}!" \
    -sampling-factor "$sampling" nadir_temp.jpg

  # Appliquer le nadir
  jpegtran -copy all -optimize -progressive -drop +0+"$nadir_offset" nadir_temp.jpg "$img" > "$output"

  if [ $? -ne 0 ]; then
    rm -f nadir_temp.jpg
    continue
  fi

  rm "$SRC_DIR/$filename"
  rm -f nadir_temp.jpg
done

echo -e "\n✅ Traitement terminé."
