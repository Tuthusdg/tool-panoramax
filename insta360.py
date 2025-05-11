import cv2
import os
import glob
import subprocess
import json
from datetime import timedelta
from dateutil import parser
from tqdm import tqdm
from PIL import Image
import piexif


def get_creation_time(video_path):
    try:
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            video_path,
        ]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        metadata = json.loads(result.stdout)
        creation_str = metadata.get("format", {}).get("tags", {}).get("creation_time")
        if not creation_str:
            print("⛔ Aucun champ 'creation_time' trouvé.")
            return None
        return parser.isoparse(creation_str)
    except Exception as e:
        print(f"⚠️ Erreur récupération creation_time: {e}")
        return None


def save_image_with_exif(image_path, frame, datetime_obj):
    temp_path = image_path + ".tmp.jpg"
    cv2.imwrite(temp_path, frame)
    img = Image.open(temp_path)
    exif_dict = {
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: datetime_obj.strftime("%Y:%m:%d %H:%M:%S")
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, "jpeg", exif=exif_bytes)
    os.remove(temp_path)


def extract_all_real_photos(input_dir):
    output_dir = os.path.join(".", "images_sortie")
    os.makedirs(output_dir, exist_ok=True)

    video_files = []
    for ext in ("*.MP4", "*.mp4", "*.360", "*.LRV"):
        video_files.extend(glob.glob(os.path.join(input_dir, ext)))

    if not video_files:
        print(f"Aucune vidéo trouvée dans : {input_dir}")
        return

    for video_path in video_files:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Impossible d’ouvrir : {video_path}")
            continue

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        name = os.path.splitext(os.path.basename(video_path))[0]
        creation_dt = get_creation_time(video_path)
        if not creation_dt:
            print(f"⚠️ Pas de date pour : {video_path}")
            continue

        print(f"\n📸 Extraction de {total_frames} images ({fps} FPS)...")
        progress = tqdm(total=total_frames, desc=name)

        for frame_index in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            # 1 frame = 1 seconde réelle
            timestamp_img = creation_dt + timedelta(seconds=frame_index)

            output_filename = f"{name}_{frame_index:05d}.jpg"
            output_path = os.path.join(output_dir, output_filename)

            save_image_with_exif(output_path, frame, timestamp_img)
            progress.update(1)

        cap.release()
        progress.close()

    print("✅ Extraction complète.")


# Appel du script
extract_all_real_photos("vids/")
