#!/usr/bin/env python3
"""
Augmentation CIBLÉE des classes rares dans Merged_dataset/train uniquement.

Ne touche JAMAIS valid/ ni test/ : on n'augmente que les données
d'entraînement, sinon l'évaluation du modèle devient faussée.

Pré-requis :
    pip install albumentations opencv-python-headless

Usage :
    python augment_minority_classes.py
"""

import os
import random
import hashlib
import cv2
from pathlib import Path
from collections import defaultdict
import albumentations as A

random.seed(42)

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------

MERGED_DIR = "Merged_dataset"          # doit contenir train/images, train/labels
TRAIN_IMAGES = Path(MERGED_DIR) / "train" / "images"
TRAIN_LABELS = Path(MERGED_DIR) / "train" / "labels"

FINAL_CLASSES = [
    "Scratch", "Dent", "Glass_Crack", "Car_Part_Crack", "Lamp_Crack",
    "Lamp_Broken", "Side_Mirror_Damage", "Detachment", "Flat_Tire",
    "Paint_Defect", "Tiny_Damage",
]

# Combien de copies augmentées générer PAR IMAGE contenant la classe.
# multiplier=1 -> pas d'augmentation. multiplier=10 -> 9 copies en plus par image.
# Seules les classes sous-représentées ont un multiplier > 1.
AUGMENT_MULTIPLIER = {
    "Scratch":             1,
    "Dent":                1,
    "Glass_Crack":         1,
    "Car_Part_Crack":      5,   # 416  -> ~2080
    "Lamp_Crack":         12,   # 149  -> ~1788
    "Lamp_Broken":         1,
    "Side_Mirror_Damage":  3,   # 750  -> ~2250
    "Detachment":          6,   # 357  -> ~2142
    "Flat_Tire":           4,   # 554  -> ~2216
    "Paint_Defect":       15,   # 112  -> ~1680
    "Tiny_Damage":        20,   # 64   -> ~1280
}

IMG_EXTS = {".jpg", ".jpeg", ".png"}

# Pipeline d'augmentation — bbox_params en format "yolo" = même format que
# nos fichiers labels (class x_center y_center width height, normalisés).
transform = A.Compose(
    [
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=10, border_mode=cv2.BORDER_REPLICATE, p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.25, contrast_limit=0.25, p=0.6),
        A.HueSaturationValue(hue_shift_limit=8, sat_shift_limit=20, val_shift_limit=10, p=0.4),
        A.GaussianBlur(blur_limit=(3, 5), p=0.2),
        A.GaussNoise(std_range=(0.02, 0.06), p=0.2),
        A.RandomShadow(p=0.15),
    ],
    bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"], min_visibility=0.3),
)


def clip_yolo_box(x, y, w, h, eps=1e-6):
    """Recadre une box YOLO (x_center, y_center, w, h normalisés) dans [0,1].
    Certaines annotations Roboflow source dépassent légèrement le cadre
    (x_max ou y_max > 1.0, ou x_min/y_min < 0) -> albumentations les refuse
    telles quelles. On les recadre proprement au lieu de les jeter."""
    x_min = max(0.0, x - w / 2)
    y_min = max(0.0, y - h / 2)
    x_max = min(1.0, x + w / 2)
    y_max = min(1.0, y + h / 2)

    new_w = x_max - x_min
    new_h = y_max - y_min
    if new_w <= eps or new_h <= eps:
        return None  # box devenue vide/dégénérée après clip -> on l'ignore

    new_x = x_min + new_w / 2
    new_y = y_min + new_h / 2
    # clamp final pour éviter les artefacts flottants pile sur 0.0/1.0
    new_x = min(max(new_x, eps), 1 - eps)
    new_y = min(max(new_y, eps), 1 - eps)
    new_w = min(new_w, 1.0)
    new_h = min(new_h, 1.0)
    return [new_x, new_y, new_w, new_h]


def read_label(path):
    boxes, classes = [], []
    if not path.exists():
        return boxes, classes
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            cls = int(parts[0])
            x, y, w, h = map(float, parts[1:5])
            clipped = clip_yolo_box(x, y, w, h)
            if clipped is None:
                continue
            classes.append(cls)
            boxes.append(clipped)
    return boxes, classes


def write_label(path, boxes, classes):
    with open(path, "w", encoding="utf-8") as f:
        for cls, (x, y, w, h) in zip(classes, boxes):
            f.write(f"{int(cls)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def find_image_path(stem):
    for ext in IMG_EXTS:
        p = TRAIN_IMAGES / (stem + ext)
        if p.exists():
            return p
    return None


def main():
    if not TRAIN_LABELS.exists():
        print(f"ERREUR: {TRAIN_LABELS} introuvable. Lance ce script depuis le dossier "
              f"qui contient '{MERGED_DIR}/'.")
        return

    # 1) index: pour chaque classe finale, quelles images (stem) la contiennent
    images_with_class = defaultdict(set)
    label_files = list(TRAIN_LABELS.glob("*.txt"))
    before_counts = defaultdict(int)

    for lbl_path in label_files:
        boxes, classes = read_label(lbl_path)
        for cls in classes:
            class_name = FINAL_CLASSES[cls]
            images_with_class[class_name].add(lbl_path.stem)
            before_counts[class_name] += 1

    print("Comptage AVANT augmentation :")
    for name in FINAL_CLASSES:
        print(f"    {name:20s}: {before_counts.get(name, 0)}")

    # 2) génération des copies augmentées, classe par classe
    after_counts = defaultdict(int, before_counts)
    total_generated = 0

    for class_name, multiplier in AUGMENT_MULTIPLIER.items():
        if multiplier <= 1:
            continue
        stems = sorted(images_with_class.get(class_name, []))
        if not stems:
            print(f"[{class_name}] aucune image trouvée, skip.")
            continue

        n_copies = multiplier - 1
        print(f"[{class_name}] {len(stems)} images sources -> {n_copies} copie(s) chacune")

        for stem in stems:
            img_path = find_image_path(stem)
            if img_path is None:
                continue
            label_path = TRAIN_LABELS / (stem + ".txt")
            boxes, classes = read_label(label_path)
            if not boxes:
                continue

            image = cv2.imread(str(img_path))
            if image is None:
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            for i in range(n_copies):
                try:
                    result = transform(image=image, bboxes=boxes, class_labels=classes)
                except Exception as e:
                    print(f"    Avertissement: augmentation échouée sur {stem} ({e}), skip.")
                    continue

                new_boxes = result["bboxes"]
                new_classes = result["class_labels"]
                if not new_boxes:
                    # toutes les boxes sont sorties du cadre après transform -> on garde l'original
                    continue

                # Nom court : évite de dépasser la limite Windows (~260 caractères)
                # en concaténant le préfixe avec un nom Roboflow parfois très long.
                short_id = hashlib.md5(f"{stem}_{i}".encode()).hexdigest()[:10]
                new_stem = f"aug_{class_name[:12]}_{short_id}"
                new_img = cv2.cvtColor(result["image"], cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(TRAIN_IMAGES / (new_stem + img_path.suffix)), new_img)
                write_label(TRAIN_LABELS / (new_stem + ".txt"), new_boxes, new_classes)

                for c in new_classes:
                    after_counts[FINAL_CLASSES[int(c)]] += 1
                total_generated += 1

    print(f"\nImages augmentées générées : {total_generated}")
    print("\nComptage APRÈS augmentation :")
    for name in FINAL_CLASSES:
        print(f"    {name:20s}: avant={before_counts.get(name,0):6d}  "
              f"après={after_counts.get(name,0):6d}")


if __name__ == "__main__":
    main()