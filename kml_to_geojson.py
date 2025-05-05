import xml.etree.ElementTree as ET
import json
import re

def converter_kml():
    with open("ton_fichier.kml", "r", encoding="utf-8") as f:
        tree = ET.parse(f)

    root = tree.getroot()

    # Namespace KML standard
    ns = {'kml': "http://www.opengis.net/kml/2.2"}

    # Trouver tous les Placemarks
    placemarks = root.findall('.//kml:Placemark', ns)

    features = []

    for placemark in placemarks:
        # Chercher la description (timestamp)
        description_elem = placemark.find('kml:description', ns)
        if description_elem is None:
            continue

        description_text = description_elem.text or ""

        # Utiliser une regex pour extraire la date/heure
        match = re.search(r'Time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', description_text)
        if not match:
            continue  # Pas de timestamp trouvé

        timestamp = match.group(1)

        # Chercher les coordonnées
        coord_elem = placemark.find('.//kml:Point/kml:coordinates', ns)
        if coord_elem is None:
            continue

        coord_text = coord_elem.text.strip()
        lon, lat, *alt = map(float, coord_text.split(','))

        # Altitude peut ne pas exister
        alt_value = alt[0] if alt else 0.0

        # Créer le Feature GeoJSON
        feature = {
            "type": "Feature",
            "properties": {
                "timestamp": timestamp
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat, alt_value]
            }
        }
        features.append(feature)

    # Génération du GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    # Sauvegarde dans un fichier
    with open("output.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

    print("✅ Conversion terminée ! Fichier : output.geojson")
