import cv2
import numpy as np

def auto_canny(gray, sigma=0.33):
    v = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(gray, lower, upper)

def contour_mask_from_edges(edges, min_area=500):
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered = [c for c in cnts if cv2.contourArea(c) >= min_area]
    return filtered

def rotated_box(contour):
    rect = cv2.minAreaRect(contour)  # (center(x,y), (width, height), angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    (w, h) = rect[1]
    width_px = max(w, h)
    height_px = min(w, h)
    return box, width_px, height_px, rect

def centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return (0,0)
    cx = int(M["m10"]/M["m00"])
    cy = int(M["m01"]/M["m00"])
    return (cx, cy)
