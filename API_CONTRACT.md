# API & WebSocket Contract: Real-Time Object Detection

This document specifies the communication contract between the VisionStream frontend client and the FastAPI backend service.

---

## 1. Architecture Overview

VisionStream supports two complementary video processing flows:

1. **Client-Side Browser Webcam (Default & Privacy-Preserving)**
   - The browser captures video frames via HTML5 `getUserMedia()`.
   - The video is rendered locally with zero latency in an HTML5 `<video>` element.
   - Throttled frames are compressed to JPEG blobs and streamed over WebSocket (`/ws/detect`) with client-side backpressure control (only transmitting the next frame after the previous inference response is received).
   - The backend processes frames in-memory and returns detection coordinates, confidence scores, and metrics.
   - Bounding boxes are drawn onto an HTML5 `<canvas>` overlaid on top of the `<video>` element.
   - **Privacy Benefit**: Video frames never leave transient memory and are never persisted to disk or external servers.

2. **Server-Side Stream / IP Camera Mode**
   - The backend captures video via OpenCV `cv2.VideoCapture` from an RTSP, HTTP/HTTPS MJPEG stream, or video source.
   - A single-slot bounded buffer (`Queue(maxsize=1)`) ensures that whenever the inference loop reads a frame, it always gets the newest frame (stale frames are automatically dropped).
   - Detections and frame previews are streamed over `/ws/stream` or `/api/stream/video`.

---

## 2. REST Endpoints

### 2.1 Health & Service Info
- **URL**: `GET /api/health`
- **Description**: Returns detector loading status, current active model, and session count.
- **Response**: `200 OK`
```json
{
  "status": "healthy",
  "model_loaded": true,
  "current_model": "yolov8n.pt",
  "active_sessions": 1,
  "device": "cpu",
  "version": "1.0.0"
}
```

### 2.2 System Configuration
- **URL**: `GET /api/config`
- **Description**: Returns allowed model names, default thresholds, and device configuration.
- **Response**: `200 OK`
```json
{
  "default_model": "yolov8n.pt",
  "allowed_models": ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"],
  "default_confidence": 0.45,
  "default_iou": 0.45,
  "max_stream_fps": 30,
  "device": "cpu"
}
```

### 2.3 Session Management

#### Start Session
- **URL**: `POST /api/session/start`
- **Request Body**:
```json
{
  "source_type": "client",          // "client" | "webcam" | "stream"
  "device_index": 0,               // Optional server camera index
  "stream_url": null,              // Optional IP camera/RTSP URL
  "model_name": "yolov8n.pt",       // Optional model selection
  "confidence_threshold": 0.45,     // Optional float (0.01 - 1.0)
  "iou_threshold": 0.45             // Optional float (0.01 - 1.0)
}
```
- **Response**: `200 OK`
```json
{
  "session_id": "761c56b7-58fb-4dd1-a1b9-3c72199b45e7",
  "state": "running",
  "source_type": "client",
  "model_name": "yolov8n.pt",
  "confidence_threshold": 0.45,
  "iou_threshold": 0.45,
  "fps": 0.0,
  "inference_ms": 0.0,
  "object_count": 0,
  "uptime_seconds": 0.0,
  "error_message": null
}
```

#### Pause Session
- **URL**: `POST /api/session/pause?session_id={id}`
- **Response**: `200 OK`
```json
{
  "session_id": "761c56b7-58fb-4dd1-a1b9-3c72199b45e7",
  "state": "paused",
  ...
}
```

#### Resume Session
- **URL**: `POST /api/session/resume?session_id={id}`
- **Response**: `200 OK`
```json
{
  "session_id": "761c56b7-58fb-4dd1-a1b9-3c72199b45e7",
  "state": "running",
  ...
}
```

#### Stop Session
- **URL**: `POST /api/session/stop?session_id={id}`
- **Description**: Releases camera and capture resources.
- **Response**: `200 OK`
```json
{
  "session_id": "761c56b7-58fb-4dd1-a1b9-3c72199b45e7",
  "state": "stopped",
  ...
}
```

#### Update Thresholds
- **URL**: `PATCH /api/session/thresholds?session_id={id}`
- **Request Body**:
```json
{
  "confidence_threshold": 0.60,
  "iou_threshold": 0.50
}
```

#### Session Status
- **URL**: `GET /api/session/status?session_id={id}`
- **Response**: `200 OK` with `SessionStatus` payload.

---

## 3. WebSocket Protocols

### 3.1 Client Detection WebSocket: `/ws/detect`

#### Client-to-Server Messages
1. **Binary JPEG Frame**:
   - Direct raw JPEG image bytes sent as WebSocket binary (`arraybuffer`).
2. **JSON Frame with Base64**:
```json
{
  "type": "frame",
  "image": "data:image/jpeg;base64,...",
  "confidence": 0.5,
  "iou": 0.45
}
```
3. **Threshold Update**:
```json
{
  "type": "update_thresholds",
  "confidence": 0.55,
  "iou": 0.40
}
```
4. **Heartbeat / Ping**:
```json
{
  "type": "ping"
}
```

#### Server-to-Client Responses
1. **Detections Payload**:
```json
{
  "type": "detections",
  "timestamp": 1791388500.12,
  "inference_ms": 22.4,
  "fps": 29.1,
  "object_count": 2,
  "frame_width": 1280,
  "frame_height": 720,
  "detections": [
    {
      "label": "person",
      "confidence": 0.924,
      "class_id": 0,
      "box": [120.5, 80.2, 450.8, 680.1],
      "box_normalized": [0.0941, 0.1114, 0.3522, 0.9446],
      "color": "#22c55e"
    },
    {
      "label": "cell phone",
      "confidence": 0.812,
      "class_id": 67,
      "box": [280.1, 310.4, 345.6, 420.9],
      "box_normalized": [0.2188, 0.4311, 0.2700, 0.5846],
      "color": "#3b82f6"
    }
  ]
}
```
2. **Heartbeat Pong**:
```json
{
  "type": "pong",
  "timestamp": 1791388500.15
}
```
3. **Error Payload**:
```json
{
  "type": "error",
  "code": "DECODE_ERROR",
  "message": "Could not decode image frame: Corrupted buffer"
}
```

---

## 4. Reconnection & Resilience Policy

- **Backpressure Handling**: The client only sends the next video frame if `isAwaitingResponse === false`. If inference takes longer than frame capture rate, subsequent frames are dropped client-side so the queue length is always strictly $\le 1$.
- **Automatic Reconnection**: Upon socket closure, the client initiates reconnection using exponential backoff:
  - Attempt 1: 1.0s
  - Attempt 2: 1.5s
  - Attempt 3: 2.25s
  - Max delay capped at 10.0s.
- **Heartbeat Watchdog**: Ping frames are transmitted every 15 seconds; connections with no response are reset.
- **Graceful Cleanup**: Backend `lifespan` handler and `POST /api/session/stop` release all OpenCV `VideoCapture` objects and thread workers.
