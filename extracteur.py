import cv2
import os
from tqdm import tqdm


def extract_frames_every_second(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la vidéo.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(frame_count / fps)

    print(f"Durée vidéo : {duration} secondes — Extraction d'une image par seconde...")

    for current_second in tqdm(range(duration), desc="Extraction"):
        cap.set(cv2.CAP_PROP_POS_MSEC, current_second * 1000)
        ret, frame = cap.read()
        if not ret:
            break
        output_path = os.path.join(output_dir, f"frame_{current_second:04d}.jpg")
        cv2.imwrite(output_path, frame)

    cap.release()
    print("✅ Extraction terminée.")


# Exemple
extract_frames_every_second("video_entree.mp4", "images_sortie")
