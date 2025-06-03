import os
import subprocess
import json
from GPSPhoto import gpsphoto
import geopandas as gpd
import pandas as pd
from bisect import bisect_left
from tqdm import tqdm


# 🔍 Lecture EXIF avec exiftool
def recup_date_img(nom_img):
    try:
        cmd = ["exiftool", "-j", "-DateTimeOriginal", nom_img]
        output = subprocess.check_output(cmd)
        data = json.loads(output)[0]
        datetime_original = data.get("DateTimeOriginal")
        if datetime_original:
            return datetime_original
        else:
            print(f"❌ Aucun DateTimeOriginal trouvé dans {nom_img}.")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction EXIF pour {nom_img} : {e}")
        return None


# 📍 Lecture du fichier GeoJSON contenant les points GPS
def parse_geojson(nom_geojson):
    data = gpd.read_file(nom_geojson)
    points = []
    for row in data.itertuples():
        timestamp = pd.to_datetime(row.timestamp, errors="coerce")
        if pd.isna(timestamp):
            continue
        point = {
            "datetime": timestamp.strftime("%Y:%m:%d %H:%M:%S"),
            "latitude": row.geometry.y,
            "longitude": row.geometry.x,
        }
        points.append(point)
    print(f"✅ {len(points)} points extraits depuis le GeoJSON.")
    return points


# 🕓 Trouver le point GPS le plus proche d'un timestamp de photo
def find_closest_gps(points, photo_time):
    if not points:
        raise ValueError("❌ Aucun point GPS disponible.")

    try:
        photo_dt = pd.to_datetime(
            photo_time, format="%Y:%m:%d %H:%M:%S", errors="raise"
        )
    except Exception as e:
        print(f"❌ Erreur lors du parsing de la date photo : {photo_time} → {e}")
        return None

    times = []
    valid_points = []
    for p in points:
        try:
            dt = pd.to_datetime(
                p["datetime"], format="%Y:%m:%d %H:%M:%S", errors="raise"
            )
            times.append(dt)
            valid_points.append(p)
        except Exception as e:
            print(f"⚠️ Timestamp GPS invalide ignoré : {p['datetime']} → {e}")
            continue

    if not times:
        raise ValueError("❌ Aucun timestamp GPS valide.")

    pos = bisect_left(times, photo_dt)

    if pos == 0:
        closest = valid_points[0]
    elif pos == len(times):
        closest = valid_points[-1]
    else:
        before, after = valid_points[pos - 1], valid_points[pos]
        before_dt = times[pos - 1]
        after_dt = times[pos]

        closest = (
            before
            if abs((before_dt - photo_dt).total_seconds())
            <= abs((after_dt - photo_dt).total_seconds())
            else after
        )

    diff = abs(
        (
            pd.to_datetime(closest["datetime"], format="%Y:%m:%d %H:%M:%S") - photo_dt
        ).total_seconds()
    )
    return closest if diff <= 0.5 else None


# 🧭 Met à jour les métadonnées EXIF GPS et horodatage
def update_exif(photo_filename, infos):
    image_dir = os.path.dirname(photo_filename)
    changed_folder = os.path.join(image_dir, "changed")
    os.makedirs(changed_folder, exist_ok=True)

    photo = gpsphoto.GPSPhoto(photo_filename)
    adjusted_time = pd.to_datetime(
        infos["datetime"], format="%Y:%m:%d %H:%M:%S", errors="raise"
    ) - pd.Timedelta(hours=2)

    correct_time = adjusted_time.strftime("%Y:%m:%d %H:%M:%S")
    info = gpsphoto.GPSInfo((infos["latitude"], infos["longitude"]), 0, correct_time)

    output_path = os.path.join(changed_folder, os.path.basename(photo_filename))
    photo.modGPSData(info, output_path)


# 🧠 Fonction principale
def main():
    points = parse_geojson("output.geojson")

    input_folder = "img_to_be_changed"
    images_to_process = [
        img
        for img in os.listdir(input_folder)
        if img.lower().endswith((".jpg", ".jpeg"))
    ]

    for image in tqdm(images_to_process, desc="Traitement des images", unit="image"):
        image_path = os.path.join(input_folder, image)
        date_img = recup_date_img(image_path)

        if date_img is None:
            unchanged_folder = os.path.join(input_folder, "unchanged")
            os.makedirs(unchanged_folder, exist_ok=True)
            os.rename(image_path, os.path.join(unchanged_folder, image))
            continue

        closest = find_closest_gps(points, photo_time=date_img)

        if closest is None:
            unchanged_folder = os.path.join(input_folder, "unchanged")
            os.makedirs(unchanged_folder, exist_ok=True)
            os.rename(image_path, os.path.join(unchanged_folder, image))
        else:
            update_exif(image_path, closest)

    print("\n✅ Le programme s'est terminé correctement.")


# 🏁 Lancer le script
if __name__ == "__main__":
    main()
