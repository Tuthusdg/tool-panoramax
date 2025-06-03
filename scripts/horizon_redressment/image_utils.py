# image_utils.py

import cv2
import piexif
import shutil
import os


def read_image_with_exif(path):
    img = cv2.imread(path)
    exif_dict = None
    try:
        exif_dict = piexif.load(path)
    except Exception:
        # Pas de métadonnées ou erreur de lecture, on ignore
        pass
    return img, exif_dict


def write_image_with_exif(img, path, exif_dict=None):
    # Sauvegarde temporaire sans exif
    tmp_path = path + ".tmp.jpg"
    cv2.imwrite(tmp_path, img)
    if exif_dict is not None:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, tmp_path)
    os.replace(tmp_path, path)


def copy_exif(src_path, dst_path):
    try:
        exif_dict = piexif.load(src_path)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, dst_path)
    except Exception:
        # Pas d'exif ou erreur, on ignore
        pass


def move_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.move(src_path, dst_path)
