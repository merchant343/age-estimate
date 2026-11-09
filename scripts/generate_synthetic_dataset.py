"""Generate a legally safe, reproducible synthetic evaluation set.
Images are generated locally and are not committed to Git."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "synthetic_dataset"
SEED = 20261109
AGE_BINS = [(0, 6), (7, 11), (12, 14), (15, 17), (18, 29)]

def main():
    random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    font = ImageFont.load_default()
    for i in range(100):
        lo, hi = AGE_BINS[i % len(AGE_BINS)]
        age = random.randint(lo, hi)
        phase = "tune" if i < 30 else "final"
        image = Image.new("RGB", (224, 336), (20 + (i * 17) % 180, 30 + (i * 29) % 150, 60 + (i * 41) % 150))
        draw = ImageDraw.Draw(image)
        for y in range(0, 336, 16):
            draw.rectangle((0, y, 224, y + 8), fill=((i * 9 + y) % 255, (i * 5 + 70) % 255, (i * 3 + 120) % 255))
        draw.rectangle((12, 120, 212, 220), outline="white", width=3)
        draw.text((22, 145), "SYNTHETIC COVER", fill="white", font=font)
        draw.text((22, 165), f"AGE GROUP {lo}-{hi}", fill="white", font=font)
        image.save(OUT / f"sample_{i:03d}.png")
        rows.append({"id": f"sample_{i:03d}", "path": str(OUT / f"sample_{i:03d}.png"), "age": age, "age_min": lo, "age_max": hi, "split": phase, "synthetic": True, "seed": SEED})
    with (OUT / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    print(f"SYNTHETIC_DATASET_OK count={len(rows)} tune=30 final=70 seed={SEED}")

if __name__ == "__main__": main()
