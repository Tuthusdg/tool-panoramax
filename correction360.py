import cv2
import numpy as np


def equirectangular_rotate(image_path, roll_deg=0, pitch_deg=0, yaw_deg=0):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)

    lon = np.linspace(-np.pi, np.pi, w, endpoint=False)
    lat = np.linspace(-np.pi / 2, np.pi / 2, h)
    lon, lat = np.meshgrid(lon, lat)

    x = np.cos(lat) * np.sin(lon)
    y = np.sin(lat)
    z = np.cos(lat) * np.cos(lon)
    xyz = np.stack([x, y, z], axis=-1)

    def rot_matrix(axis, angle):
        c, s = np.cos(angle), np.sin(angle)
        if axis == "x":
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == "y":
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == "z":
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    R = rot_matrix("z", roll) @ rot_matrix("x", pitch) @ rot_matrix("y", yaw)
    xyz_rot = xyz @ R.T

    lon_new = np.arctan2(xyz_rot[..., 0], xyz_rot[..., 2])
    lat_new = np.arcsin(xyz_rot[..., 1])

    x_map = ((lon_new + np.pi) / (2 * np.pi) * w).astype(np.float32)
    y_map = ((lat_new + np.pi / 2) / np.pi * h).astype(np.float32)

    result = cv2.remap(
        img, x_map, y_map, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP
    )
    return result


def extract_horizon_strip(eqr_img, band_height=0.2):
    h, w = eqr_img.shape[:2]
    band = int(h * band_height / 2)
    y_center = h // 2
    return eqr_img[y_center - band : y_center + band]


def detect_dominant_angle(image_strip):
    gray = cv2.cvtColor(image_strip, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is None:
        print("❌ Aucune ligne détectée.")
        return 0

    angles = []
    for rho, theta in lines[:, 0]:
        angle_deg = np.degrees(theta)
        # Garder les lignes proches de l’horizontale
        if 80 < angle_deg < 100 or 260 < angle_deg < 280:
            angles.append(angle_deg)

    if not angles:
        print("❌ Aucune ligne horizontale trouvée.")
        return 0

    avg_angle = np.mean(angles)
    correction = avg_angle - 90
    print(
        f"✅ Angle moyen détecté : {avg_angle:.2f}° → Correction : {-correction:.2f}°"
    )
    return correction


if __name__ == "__main__":
    input_img_path = "photo.jpg"  # ← Remplace par ton image
    output_img_path = "corrected.jpg"

    original_img = cv2.imread(input_img_path)
    horizon_band = extract_horizon_strip(original_img)
    roll_correction = detect_dominant_angle(horizon_band)

    corrected_img = equirectangular_rotate(input_img_path, roll_deg=-roll_correction)
    cv2.imwrite(output_img_path, corrected_img)

    print("✅ Image redressée enregistrée :", output_img_path)
