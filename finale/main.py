import os
from tqdm import tqdm
from image_utils import read_image_with_exif, write_image_with_exif
from constants import (
    OUTPUT_DIR,
    SLOPE_ERROR_THRESHOLD,
    CERTAIN_DIR,
    UNCERTAIN_DIR,
)
from alignment import binary_search_roll
import csv


def auto_align_roll_for_folder(
    input_dir, output_dir=OUTPUT_DIR, seuil=SLOPE_ERROR_THRESHOLD
):
    os.makedirs(CERTAIN_DIR, exist_ok=True)
    os.makedirs(UNCERTAIN_DIR, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".jpg")]

    print(f"[INFO] Traitement de {len(files)} images dans '{input_dir}'...")

    csv_file = os.path.join(output_dir, "results.csv")
    file_exists = os.path.isfile(csv_file)

    for file_index, file_name in enumerate(
        tqdm(files, unit="image", dynamic_ncols=True, leave=True)
    ):
        tqdm.write(f"[INFO] Traitement de : {file_name}")

        full_path = os.path.join(input_dir, file_name)
        img, exif = read_image_with_exif(full_path)
        if img is None:
            tqdm.write(f"[ERREUR] Impossible de lire : {file_name}")
            continue

        h, w = img.shape[:2]

        best_angle, best_error, best_img, amplitude, phase = binary_search_roll(
            img, w, h, -15, 15
        )

        tqdm.write(
            f"[RESULT] Angle : {best_angle:.2f}° | Erreur pente : {best_error:.4f} | Amplitude : {amplitude} | Phase : {phase:.2f}"
        )

        if best_error < seuil:
            output_subdir = CERTAIN_DIR
            out_path = os.path.join(
                output_subdir, f"{os.path.splitext(file_name)[0]}_redresse.jpg"
            )
            write_image_with_exif(best_img, out_path, exif)
            os.remove(full_path)
            tqdm.write(
                f"[OK] Image enregistrée dans : {output_subdir} (original supprimé)"
            )

            # Écrire dans CSV immédiatement après traitement de l'image certaine
            with open(csv_file, "a", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "filename",
                        "angle",
                        "slope_error",
                        "amplitude",
                        "phase",
                        "output_subdir",
                    ],
                )
                if not file_exists:
                    writer.writeheader()
                    file_exists = True  # éviter d'écrire le header plusieurs fois
                writer.writerow(
                    {
                        "filename": file_name,
                        "angle": best_angle,
                        "slope_error": best_error,
                        "amplitude": amplitude,
                        "phase": phase,
                        "output_subdir": output_subdir,
                    }
                )

        else:
            output_subdir = UNCERTAIN_DIR
            out_path = os.path.join(
                output_subdir, f"{os.path.splitext(file_name)[0]}_redresse.jpg"
            )
            write_image_with_exif(best_img, out_path, exif)
            tqdm.write(
                f"[ATTENTION] Image enregistrée dans : {output_subdir} (original conservé)"
            )

    print(f"\n[INFO] Traitement terminé. Résultats enregistrés dans {csv_file}")
