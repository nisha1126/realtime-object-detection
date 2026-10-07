"""Unit tests for session management and state transitions."""

import pytest
from app.services.session_manager import SessionManager
from app.schemas.detection import SessionStartRequest


def test_session_lifecycle():
    manager = SessionManager.get_instance()
    req = SessionStartRequest(
        source_type="client",
        confidence_threshold=0.5,
        iou_threshold=0.45,
    )
    session = manager.create_session(req)

    assert session.session_id is not None
    assert session.state == "running"
    assert session.confidence_threshold == 0.5

    # Test update metrics
    session.update_metrics(inference_ms=25.0, count=2)
    assert session.inference_ms == 25.0
    assert session.object_count == 2

    # Pause
    status = manager.pause_session(session.session_id)
    assert status.state == "paused"

    # Resume
    status = manager.resume_session(session.session_id)
    assert status.state == "running"

    # Stop
    status = manager.stop_session(session.session_id)
    assert status.state == "stopped"


def test_invalid_session_pause():
    manager = SessionManager.get_instance()
    with pytest.raises(ValueError):
        manager.pause_session("non_existent_session_id_12345")
