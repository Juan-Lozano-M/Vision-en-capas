"""Genera una imagen de ejemplo con figuras separadas y colores conocidos."""

from pathlib import Path
import cv2
import numpy as np


def main() -> None:
    canvas = np.full((620, 1050, 3), (235, 240, 236), dtype=np.uint8)
    cv2.circle(canvas, (175, 260), 105, (70, 70, 220), -1)          # rojo
    cv2.rectangle(canvas, (355, 160), (545, 350), (50, 180, 70), -1)  # verde
    triangle = np.array([[735, 145], [620, 360], [850, 360]], np.int32)
    cv2.fillPoly(canvas, [triangle], (230, 130, 40))                 # azul
    cv2.rectangle(canvas, (905, 180), (1000, 390), (30, 210, 235), -1)  # amarillo
    cv2.circle(canvas, (240, 505), 65, (180, 80, 180), -1)           # morado
    cv2.rectangle(canvas, (430, 450), (620, 555), (40, 140, 240), -1)   # naranja
    output = Path(__file__).resolve().parents[1] / "assets" / "example_shapes.png"
    output.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(output), canvas)
    print(f"Imagen creada en {output}")


if __name__ == "__main__":
    main()

