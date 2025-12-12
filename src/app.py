import cv2
import argparse
from measure import process_image

def get_args():
    p = argparse.ArgumentParser(description="Measure object size with a known reference width (mm)")
    p.add_argument("--image", required=True, help="path to input image")
    p.add_argument("--known_width_mm", type=float, required=True, help="known width (mm) of reference object")
    p.add_argument("--ref_hint", type=str, default=None, help="optional: left|right|top|bottom")
    p.add_argument("--canny", nargs=2, type=int, default=[50,150], help="Canny thresholds, e.g., 50 150")
    p.add_argument("--min_area", type=int, default=500, help="minimum contour area")
    p.add_argument("--out", default="./docs/images/out.jpg", help="output image path")
    p.add_argument("--debug", action="store_true", help="save intermediate images")
    return p.parse_args()

if __name__ == "__main__":
    args = get_args()
    img = cv2.imread(args.image)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {args.image}")
    debug_prefix = "./docs/images/debug" if args.debug else None
    result = process_image(
        img, 
        known_width_mm=args.known_width_mm, 
        canny=(args.canny[0], args.canny[1]),
        min_area=args.min_area,
        ref_hint=args.ref_hint,
        debug_prefix=debug_prefix
    )
    ok = cv2.imwrite(args.out, result)
    if not ok:
        raise RuntimeError(f"Failed to write output to {args.out}")
    print(f"Saved result to {args.out}")
