import numpy as np
import math
import cv2


def deg_to_rad(angle):
    return angle * 2.0 * math.pi / 360.0


def set_rotation_matrix(yaw, pitch, roll):
    a = deg_to_rad(yaw)
    b = deg_to_rad(pitch)
    c = deg_to_rad(roll)

    Rx = np.array(
        [[1, 0, 0], [0, math.cos(a), math.sin(a)], [0, -math.sin(a), math.cos(a)]]
    )
    Ry = np.array(
        [[math.cos(b), 0, -math.sin(b)], [0, 1, 0], [math.sin(b), 0, math.cos(b)]]
    )
    Rz = np.array(
        [[math.cos(c), math.sin(c), 0], [-math.sin(c), math.cos(c), 0], [0, 0, 1]]
    )

    return Ry @ Rx @ Rz


def compute_dewarping_vectorized(yaw, pitch, roll, width, height):
    j, i = np.meshgrid(np.arange(width), np.arange(height))
    theta = (j / width - 0.5) * 2.0 * math.pi
    phi = (i / height - 0.5) * math.pi

    x = np.cos(phi) * np.sin(theta)
    y = np.sin(phi)
    z = np.cos(phi) * np.cos(theta)

    vec = np.stack([x, y, z], axis=-1)
    R = set_rotation_matrix(yaw, pitch, roll)
    vec_rotated = vec @ R.T

    theta_new = np.arctan2(vec_rotated[..., 0], vec_rotated[..., 2])
    phi_new = np.arcsin(vec_rotated[..., 1])

    x_new = (theta_new / math.pi / 2.0 + 0.5) * width
    y_new = (phi_new / math.pi + 0.5) * height

    return x_new.astype(np.float32), y_new.astype(np.float32)


def dewarp_image(img, yaw, pitch, roll):
    height, width = img.shape[:2]
    map_x, map_y = compute_dewarping_vectorized(yaw, pitch, roll, width, height)
    return cv2.remap(
        img, map_x, map_y, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP
    )


def is_blue(img):
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    return (b > 150) & (b > g) & (b > r)


def generate_sinusoid(w, h, amplitude, phase):
    x = np.arange(w)
    return (h // 2 + amplitude * np.sin(2 * np.pi * x / w + phase)).astype(np.int32)


def score_sinusoid(blue_mask, curve):
    h, w = blue_mask.shape
    rows = np.arange(h)[:, None]
    curve_map = np.broadcast_to(curve, (h, w))
    mask_above = rows < curve_map
    return np.count_nonzero(mask_above & ~blue_mask)


def find_best_sinusoid(blue_mask, h, w):
    best_score = float("inf")
    best_curve = None
    best_amplitude = None
    best_phase = None

    for amplitude in range(20, h // 3, 20):
        for phase in np.linspace(0, 2 * np.pi, 8):
            curve = generate_sinusoid(w, h, amplitude, phase)
            score = score_sinusoid(blue_mask, curve)
            if score < best_score:
                best_score = score
                best_curve = curve
                best_amplitude = amplitude
                best_phase = phase
    return best_curve, best_amplitude, best_phase


def curve_slope_error(curve):
    x = np.arange(len(curve)).astype(np.float32)
    y = curve.astype(np.float32)
    A = np.vstack([x, np.ones_like(x)]).T
    a, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return abs(a)


def binary_search_roll(img, w, h, angle_min, angle_max, step=0.1, max_iter=20):
    best_error = float("inf")
    best_angle = 0.0
    best_img = None
    best_amplitude = None
    best_phase = None

    for _ in range(max_iter):
        mid_angle = (angle_min + angle_max) / 2.0
        left_angle = mid_angle - step
        right_angle = mid_angle + step

        # Gauche
        warped_left = dewarp_image(img, 0, 0, left_angle)
        small_left = cv2.resize(warped_left, (w // 4, h // 4))
        mask_left = is_blue(small_left)
        curve_left, amp_left, phase_left = find_best_sinusoid(mask_left, h // 4, w // 4)
        err_left = curve_slope_error(curve_left)

        # Droite
        warped_right = dewarp_image(img, 0, 0, right_angle)
        small_right = cv2.resize(warped_right, (w // 4, h // 4))
        mask_right = is_blue(small_right)
        curve_right, amp_right, phase_right = find_best_sinusoid(
            mask_right, h // 4, w // 4
        )
        err_right = curve_slope_error(curve_right)

        if err_left < err_right:
            angle_max = mid_angle
            if err_left < best_error:
                best_error = err_left
                best_angle = left_angle
                best_img = warped_left
                best_amplitude = amp_left
                best_phase = phase_left
        else:
            angle_min = mid_angle
            if err_right < best_error:
                best_error = err_right
                best_angle = right_angle
                best_img = warped_right
                best_amplitude = amp_right
                best_phase = phase_right

        if abs(angle_max - angle_min) < step:
            break

    return best_angle, best_error, best_img, best_amplitude, best_phase
