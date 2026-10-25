"""Funciones de procesamiento para detectar colores, formas y cantidades."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import cv2
import numpy as np


@dataclass
class Detection:
    """Representa un objeto identificado en la imagen."""

    object_id: int
    color: str
    shape: str
    area: float
    center_x: int
    center_y: int
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


COLOR_RANGES = {
    "rojo": [(np.array([0, 70, 50]), np.array([10, 255, 255])),
             (np.array([170, 70, 50]), np.array([180, 255, 255]))],
    "naranja": [(np.array([11, 70, 50]), np.array([25, 255, 255]))],
    "amarillo": [(np.array([26, 70, 50]), np.array([35, 255, 255]))],
    "verde": [(np.array([36, 45, 40]), np.array([85, 255, 255]))],
    "azul": [(np.array([86, 60, 40]), np.array([135, 255, 255]))],
    "morado": [(np.array([136, 45, 40]), np.array([169, 255, 255]))],
}


def resize_image(image: np.ndarray, max_width: int = 1100) -> np.ndarray:
    """Redimensiona sin deformar y limita el ancho para una respuesta ágil."""
    height, width = image.shape[:2]
    if width <= max_width:
        return image.copy()
    scale = max_width / width
    return cv2.resize(image, (max_width, int(height * scale)), interpolation=cv2.INTER_AREA)


def preprocess_image(image: np.ndarray) -> dict[str, np.ndarray]:
    """Genera las representaciones usadas durante el preprocesamiento."""
    resized = resize_image(image)
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    return {"resized": resized, "blurred": blurred, "hsv": hsv, "gray": gray}


def _mask_for_color(hsv: np.ndarray, color: str) -> np.ndarray:
    """Construye una máscara binaria para un color en el espacio HSV."""
    masks = [cv2.inRange(hsv, lower, upper) for lower, upper in COLOR_RANGES[color]]
    mask = masks[0]
    for extra_mask in masks[1:]:
        mask = cv2.bitwise_or(mask, extra_mask)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def classify_shape(contour: np.ndarray) -> tuple[str, float]:
    """Clasifica una figura a partir de la aproximación de su contorno."""
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return "desconocida", 0.0
    approximation = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    vertices = len(approximation)
    area = cv2.contourArea(contour)
    circularity = 4 * np.pi * area / (perimeter * perimeter)

    if vertices == 3:
        shape = "triángulo"
    elif vertices == 4:
        x, y, width, height = cv2.boundingRect(approximation)
        ratio = width / max(height, 1)
        shape = "cuadrado" if 0.82 <= ratio <= 1.18 else "rectángulo"
    elif vertices == 5:
        shape = "pentágono"
    elif circularity >= 0.72 or vertices > 7:
        shape = "círculo"
    else:
        shape = "forma irregular"
    confidence = min(0.99, max(0.55, circularity if shape == "círculo" else 1 - abs(vertices - 4) * 0.08))
    return shape, float(confidence)


def detect_objects(image: np.ndarray, min_area: int = 500) -> tuple[np.ndarray, list[Detection], dict[str, np.ndarray]]:
    """Detecta objetos de colores conocidos y dibuja sus etiquetas."""
    stages = preprocess_image(image)
    output = stages["resized"].copy()
    hsv = stages["hsv"]
    detections: list[Detection] = []
    next_id = 1

    for color in COLOR_RANGES:
        mask = _mask_for_color(hsv, color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            moments = cv2.moments(contour)
            center_x = int(moments["m10"] / moments["m00"]) if moments["m00"] else 0
            center_y = int(moments["m01"] / moments["m00"]) if moments["m00"] else 0
            shape, confidence = classify_shape(contour)
            detections.append(Detection(next_id, color, shape, area, center_x, center_y, confidence))
            color_bgr = {
                "rojo": (70, 70, 230), "naranja": (40, 140, 240), "amarillo": (30, 220, 240),
                "verde": (70, 190, 100), "azul": (230, 120, 60), "morado": (190, 80, 180),
            }[color]
            cv2.drawContours(output, [contour], -1, color_bgr, 4)
            # cv2.putText no renderiza UTF-8 de forma confiable; usamos texto ASCII
            # solo en la etiqueta dibujada. Los datos internos conservan el español.
            display_colors = {"rojo": "rojo", "naranja": "naranja", "amarillo": "amarillo", "verde": "verde", "azul": "azul", "morado": "morado"}
            display_shapes = {"triángulo": "triangulo", "círculo": "circulo", "rectángulo": "rectangulo", "cuadrado": "cuadrado", "pentágono": "pentagono", "forma irregular": "irregular", "desconocida": "desconocida"}
            label = f"#{next_id} {display_colors[color]} - {display_shapes.get(shape, shape)}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.58, 2)
            label_x = max(4, center_x - label_w // 2)
            label_y = max(label_h + 8, center_y - 12)
            cv2.rectangle(output, (label_x - 5, label_y - label_h - 7), (label_x + label_w + 5, label_y + 5), (15, 25, 35), -1)
            cv2.putText(output, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (245, 248, 246), 2, cv2.LINE_AA)
            next_id += 1

    detections.sort(key=lambda item: item.object_id)
    stages["edges"] = cv2.Canny(stages["gray"], 50, 150)
    stages["masks_preview"] = cv2.cvtColor(_combined_mask(hsv), cv2.COLOR_GRAY2BGR)
    return output, detections, stages


def _combined_mask(hsv: np.ndarray) -> np.ndarray:
    """Une las máscaras de color para visualizar la extracción de información."""
    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for color in COLOR_RANGES:
        combined = cv2.bitwise_or(combined, _mask_for_color(hsv, color))
    return combined


def summarize_detections(detections: list[Detection]) -> dict[str, Any]:
    """Calcula conteos por color y forma para mostrar en la interfaz."""
    by_color: dict[str, int] = {}
    by_shape: dict[str, int] = {}
    for detection in detections:
        by_color[detection.color] = by_color.get(detection.color, 0) + 1
        by_shape[detection.shape] = by_shape.get(detection.shape, 0) + 1
    return {"total": len(detections), "by_color": by_color, "by_shape": by_shape}

