import xml.etree.ElementTree as ET
import json
import re
import glob
import os


def converter_kml():
    # Chemin vers le dossier contenant les fichiers KML
    kml_folder = "kml_here/"
    kml_files = glob.glob(os.path.join(kml_folder, "*.kml"))

    if not kml_files:
        print("❌ Aucun fichier .kml trouvé dans le dossier 'kml_here/'.")
        return

    # Si un seul fichier trouvé, l'utiliser automatiquement
    if len(kml_files) == 1:
        filename = kml_files[0]
        print(f"🔍 Fichier détecté : {filename}")
    else:
        print("📂 Plusieurs fichiers .kml trouvés dans 'kml_here/':")
        for i, file in enumerate(kml_files, 1):
            print(f"{i}. {os.path.basename(file)}")
        choice = int(input("Entrez le numéro du fichier à utiliser : "))
        filename = kml_files[choice - 1]

    with open(filename, "r", encoding="utf-8") as f:
        tree = ET.parse(f)

    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = root.findall(".//kml:Placemark", ns)

    features = []

    for placemark in placemarks:
        description_elem = placemark.find("kml:description", ns)
        if description_elem is None:
            continue

        description_text = description_elem.text or ""
        match = re.search(
            r"Time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", description_text
        )
        if not match:
            continue

        timestamp = match.group(1)

        coord_elem = placemark.find(".//kml:Point/kml:coordinates", ns)
        if coord_elem is None:
            continue

        coord_text = coord_elem.text.strip()
        lon, lat, *alt = map(float, coord_text.split(","))
        alt_value = alt[0] if alt else 0.0

        feature = {
            "type": "Feature",
            "properties": {"timestamp": timestamp},
            "geometry": {"type": "Point", "coordinates": [lon, lat, alt_value]},
        }
        features.append(feature)

    geojson = {"type": "FeatureCollection", "features": features}

    output_file = "output.geojson"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

    print(f"✅ Conversion terminée ! Fichier : {output_file}")


if __name__ == "__main__":
    converter_kml()
