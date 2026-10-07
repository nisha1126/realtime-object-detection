"""WebSocket endpoint tests."""

import pytest
import numpy as np
import cv2
import base64
from starlette.testclient import TestClient
from app.main import app


def test_websocket_detect_ping_pong():
    client = TestClient(app)
    with client.websocket_connect("/ws/detect") as websocket:
        websocket.send_json({"type": "ping"})
        data = websocket.receive_json()
        assert data["type"] == "pong"
        assert "timestamp" in data


def test_websocket_detect_thresholds_update():
    client = TestClient(app)
    with client.websocket_connect("/ws/detect") as websocket:
        websocket.send_json({"type": "update_thresholds", "confidence": 0.65, "iou": 0.55})
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["confidence"] == 0.65
        assert data["iou"] == 0.55


def test_websocket_detect_frame_json():
    client = TestClient(app)
    # Generate small 160x160 test image
    img = np.zeros((160, 160, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    b64_img = base64.b64encode(buffer).decode("ascii")

    with client.websocket_connect("/ws/detect") as websocket:
        websocket.send_json({"type": "frame", "image": b64_img})
        data = websocket.receive_json()
        assert data["type"] == "detections"
        assert "inference_ms" in data
        assert "fps" in data
        assert "detections" in data
        assert data["frame_width"] == 160
        assert data["frame_height"] == 160


def test_websocket_detect_frame_binary():
    client = TestClient(app)
    img = np.zeros((160, 160, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    raw_bytes = buffer.tobytes()

    with client.websocket_connect("/ws/detect") as websocket:
        websocket.send_bytes(raw_bytes)
        data = websocket.receive_json()
        assert data["type"] == "detections"
        assert "inference_ms" in data
        assert "detections" in data
