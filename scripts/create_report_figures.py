"""Genera las figuras que documentan las etapas del flujo del informe."""

from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.image_processor import detect_objects


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def add_title(image: np.ndarray, title: str) -> np.ndarray:
    """Añade una franja de título a una imagen BGR."""
    canvas = np.full((image.shape[0] + 58, image.shape[1], 3), (28, 52, 58), dtype=np.uint8)
    canvas[58:] = image
    cv2.putText(canvas, title, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (235, 248, 242), 2, cv2.LINE_AA)
    return canvas


def main() -> None:
    original = cv2.imread(str(ASSETS / "example_shapes.png"))
    if original is None:
        raise FileNotFoundError("Ejecuta primero scripts/create_examples.py")
    result, detections, stages = detect_objects(original, min_area=500)
    cv2.imwrite(str(ASSETS / "report_original.png"), add_title(stages["resized"], "ETAPA 1 - IMAGEN ORIGINAL"))
    cv2.imwrite(str(ASSETS / "report_preprocessing.png"), add_title(stages["blurred"], "ETAPA 2 - PREPROCESAMIENTO - SUAVIZADO"))

    edges = cv2.cvtColor(stages["edges"], cv2.COLOR_GRAY2BGR)
    mask = stages["masks_preview"]
    extraction = cv2.hconcat([edges, mask])
    cv2.imwrite(str(ASSETS / "report_extraction.png"), add_title(extraction, "ETAPA 3 - EXTRACCION - BORDES Y MASCARA DE COLOR"))
    cv2.imwrite(str(ASSETS / "report_result.png"), add_title(result, f"ETAPA 4 - RESULTADO - {len(detections)} OBJETOS DETECTADOS"))
    print("Figuras del informe generadas en", ASSETS)


if __name__ == "__main__":
    main()

