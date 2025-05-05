from PIL import Image, ExifTags
from GPSPhoto import gpsphoto
import geopandas as gpd
import pandas as pd
from bisect import bisect_left
from tqdm import tqdm
import os


def recup_date_img(nom_img):
    img = Image.open(nom_img)
    img_exif = img.getexif()
    if img_exif is None:
        print(f"❌ L'image {nom_img} n'a pas de données EXIF.")
        return None
    for key, val in img_exif.items():
        if key in ExifTags.TAGS and ExifTags.TAGS[key] == "DateTime":
            return str(val)
    print(f"❌ Pas de tag DateTime trouvé dans {nom_img}.")
    return None


def parse_geojson(nom_geojson):
    data = gpd.read_file(nom_geojson)
    points = []
    for row in data.itertuples():
        timestamp = pd.to_datetime(row.timestamp, errors="coerce")
        if pd.isna(timestamp):
            continue  # Ignore les timestamps invalides
        point = {
            "datetime": timestamp.strftime("%Y:%m:%d %H:%M:%S"),
            "latitude": row.geometry.y,
            "longitude": row.geometry.x,
        }
        points.append(point)
    print(f"✅ {len(points)} points extraits depuis le GeoJSON.")
    return points


def find_closest_gps(points, photo_time):
    """Trouver le point GPS le plus proche du timestamp photo, si différence <= 0.5s."""
    if not points:
        raise ValueError("❌ Aucun point GPS disponible.")

    try:
        photo_dt = pd.to_datetime(
            photo_time, format="%Y:%m:%d %H:%M:%S", errors="raise"
        )
    except Exception as e:
        print(f"❌ Erreur lors du parsing de la date photo : {photo_time} → {e}")
        return None

    times = [
        pd.to_datetime(p["datetime"], format="%Y:%m:%d %H:%M:%S", errors="coerce")
        for p in points
    ]

    if any(pd.isna(t) for t in times):
        raise ValueError("❌ Une ou plusieurs dates GPS sont dans un format invalide.")

    pos = bisect_left(times, photo_dt)

    if pos == 0:
        closest = points[0]
    elif pos == len(points):
        closest = points[-1]
    else:
        before, after = points[pos - 1], points[pos]
        before_dt = pd.to_datetime(before["datetime"], format="%Y:%m:%d %H:%M:%S")
        after_dt = pd.to_datetime(after["datetime"], format="%Y:%m:%d %H:%M:%S")

        if abs((before_dt - photo_dt).total_seconds()) <= abs(
            (after_dt - photo_dt).total_seconds()
        ):
            closest = before
        else:
            closest = after

    closest_dt = pd.to_datetime(closest["datetime"], format="%Y:%m:%d %H:%M:%S")
    diff = abs((closest_dt - photo_dt).total_seconds())

    return closest if diff <= 0.5 else None


def update_exif(photo_filename, infos):
    image_dir = os.path.dirname(photo_filename)
    changed_folder = os.path.join(image_dir, "changed")
    os.makedirs(changed_folder, exist_ok=True)

    photo = gpsphoto.GPSPhoto(photo_filename)
    adjusted_time = pd.to_datetime(
        infos["datetime"], format="%Y:%m:%d %H:%M:%S"
    ) - pd.Timedelta(hours=2)
    correct_time = adjusted_time.strftime("%Y:%m:%d %H:%M:%S")
    info = gpsphoto.GPSInfo((infos["latitude"], infos["longitude"]), 0, correct_time)

    output_path = os.path.join(changed_folder, os.path.basename(photo_filename))
    photo.modGPSData(info, output_path)


def main():
    points = parse_geojson("output.geojson")
    os.makedirs("unchanged", exist_ok=True)

    images_to_process = os.listdir("img_to_be_changed")
    images_to_process = [
        img for img in images_to_process if img.lower().endswith((".jpg", ".jpeg"))
    ]

    for image in tqdm(images_to_process, desc="Traitement des images", unit="image"):
        image_path = os.path.join("img_to_be_changed", image)
        date_img = recup_date_img(image_path)

        if date_img is None:
            unchanged_folder = os.path.join(os.path.dirname(image_path), "unchanged")
            os.makedirs(unchanged_folder, exist_ok=True)
            os.rename(image_path, os.path.join(unchanged_folder, image))
            continue

        closest = find_closest_gps(points, photo_time=date_img)

        if closest is None:
            unchanged_folder = os.path.join(os.path.dirname(image_path), "unchanged")
            os.makedirs(unchanged_folder, exist_ok=True)
            os.rename(image_path, os.path.join(unchanged_folder, image))
        else:
            update_exif(image_path, closest)

    print("\n✅ Le programme s'est terminé correctement.")
