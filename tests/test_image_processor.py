"""Pruebas básicas del detector."""

import cv2
import numpy as np

from src.image_processor import classify_shape, detect_objects, summarize_detections


def test_classify_triangle():
    contour = np.array([[[0, 0]], [[100, 0]], [[50, 90]]], dtype=np.int32)
    shape, confidence = classify_shape(contour)
    assert shape == "triángulo"
    assert confidence > 0


def test_detects_red_circle():
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    image[:] = (240, 240, 240)
    cv2.circle(image, (150, 150), 70, (0, 0, 255), -1)
    result, detections, _ = detect_objects(image, min_area=500)
    assert result.shape == image.shape
    assert len(detections) == 1
    assert detections[0].color == "rojo"
    assert detections[0].shape == "círculo"


def test_summary_counts_colors_and_shapes():
    image = np.zeros((300, 500, 3), dtype=np.uint8)
    image[:] = (240, 240, 240)
    cv2.circle(image, (100, 150), 50, (0, 0, 255), -1)
    cv2.rectangle(image, (260, 100), (380, 200), (0, 255, 0), -1)
    _, detections, _ = detect_objects(image, min_area=500)
    summary = summarize_detections(detections)
    assert summary["total"] == 2
    assert summary["by_color"]["rojo"] == 1
    assert summary["by_color"]["verde"] == 1

