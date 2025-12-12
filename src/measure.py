import cv2
import numpy as np
from utils import auto_canny, contour_mask_from_edges, rotated_box, centroid

def choose_reference(contours, hint=None, image_shape=None):
    if not contours:
        return None, []
    if hint not in {"left","right","top","bottom", None}:
        hint = None
    if hint and image_shape is not None:
        H, W = image_shape[:2]
        if hint == "left":
            ref = min(contours, key=lambda c: centroid(c)[0])
        elif hint == "right":
            ref = max(contours, key=lambda c: centroid(c)[0])
        elif hint == "top":
            ref = min(contours, key=lambda c: centroid(c)[1])
        elif hint == "bottom":
            ref = max(contours, key=lambda c: centroid(c)[1])
        others = [c for c in contours if c is not ref]
        return ref, others
    # default: largest area is reference
    areas = [(cv2.contourArea(c), i) for i,c in enumerate(contours)]
    areas.sort(reverse=True)
    ref = contours[areas[0][1]]
    others = [contours[i] for _,i in areas[1:]]
    return ref, others

def annotate_box(img, box, text, color=(0,255,0)):
    cv2.drawContours(img, [box], 0, color, 2)
    x = int(np.min(box[:,0]))
    y = int(np.min(box[:,1])) - 10
    cv2.putText(img, text, (x, max(20,y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def process_image(img_bgr, known_width_mm=85.6, canny=(50,150), min_area=500, ref_hint=None, debug_prefix=None):
    out = img_bgr.copy()
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, canny[0], canny[1])

    if debug_prefix:
        cv2.imwrite(f"{debug_prefix}_edges.jpg", edges)

    contours = contour_mask_from_edges(edges, min_area=min_area)
    if not contours:
        cv2.putText(out, "No contours found", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return out

    ref, others = choose_reference(contours, hint=ref_hint, image_shape=img_bgr.shape)
    if ref is None:
        cv2.putText(out, "No reference contour", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return out

    # Reference box and scale
    ref_box, ref_w_px, ref_h_px, _ = rotated_box(ref)
    ref_width_px = ref_w_px  # use longer side as width
    px_per_mm = ref_width_px / known_width_mm if known_width_mm > 0 else 1.0

    annotate_box(out, ref_box, f"REF ~ {known_width_mm:.1f} mm (px:{ref_width_px:.1f})", (255,0,0))

    # Measure others
    for c in others:
        box, w_px, h_px, _ = rotated_box(c)
        width_mm = w_px / px_per_mm
        height_mm = h_px / px_per_mm
        annotate_box(out, box, f"W:{width_mm:.1f}mm  H:{height_mm:.1f}mm", (0,255,0))

    return out
