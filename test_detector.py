"""Unit tests for YOLO detector wrapper and image processing."""

import pytest
import numpy as np
import cv2
from app.models.detector import YOLODetector


def test_detector_initialization():
    detector = YOLODetector.get_instance()
    assert detector.is_loaded is True
    assert detector.model_name == "yolov8n.pt"
    assert detector.load_error is None


def test_detector_decode_image_bytes():
    # Create synthetic test image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[20:80, 20:80] = [255, 0, 0]
    _, encoded = cv2.imencode(".jpg", img)
    image_bytes = encoded.tobytes()

    decoded = YOLODetector.decode_image_bytes(image_bytes)
    assert decoded is not None
    assert decoded.shape == (100, 100, 3)


def test_detector_decode_invalid_bytes():
    with pytest.raises(ValueError):
        YOLODetector.decode_image_bytes(b"invalid_non_image_bytes")


def test_detector_inference_on_synthetic_frame():
    detector = YOLODetector.get_instance()
    # Create 320x320 synthetic frame
    frame = np.full((320, 320, 3), 128, dtype=np.uint8)

    result = detector.detect(frame, confidence_threshold=0.25, iou_threshold=0.45)
    assert result.type == "detections"
    assert result.frame_width == 320
    assert result.frame_height == 320
    assert result.inference_ms >= 0.0
    assert isinstance(result.detections, list)

    for det in result.detections:
        assert 0.0 <= det.confidence <= 1.0
        assert len(det.box) == 4
        assert len(det.box_normalized) == 4
        # Normalized coordinates should be within 0.0 to 1.0
        assert 0.0 <= det.box_normalized[0] <= 1.0
        assert 0.0 <= det.box_normalized[1] <= 1.0
        assert 0.0 <= det.box_normalized[2] <= 1.0
        assert 0.0 <= det.box_normalized[3] <= 1.0


def test_detector_empty_frame_handling():
    detector = YOLODetector.get_instance()
    with pytest.raises(ValueError):
        detector.detect(np.array([]))
