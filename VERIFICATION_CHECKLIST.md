# Verification Checklist: Real-Time Object Detection System

Use this checklist to manually verify all functionality across browsers and environments.

---

## 1. Prerequisites & Environment Check

- [ ] **Python**: Python 3.10+ (tested on Python 3.13.12).
- [ ] **Node.js**: Node.js 18+ (tested on Node v22.14.0).
- [ ] **Backend Dependencies**: `fastapi`, `uvicorn`, `opencv-python`, `ultralytics`, `torch`, `websockets`.
- [ ] **Frontend Dependencies**: React 19, Lucide React, Vite, TypeScript.

---

## 2. Backend Service Verification

- [ ] **Service Startup**:
  ```bash
  cd backend
  uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
  - Expected: Logs display `Model yolov8n.pt ready on device 'cpu'`.
- [ ] **Health Endpoint**:
  - Request `GET http://127.0.0.1:8000/api/health`
  - Expected: Returns `status: "healthy"`, `model_loaded: true`.
- [ ] **Configuration Endpoint**:
  - Request `GET http://127.0.0.1:8000/api/config`
  - Expected: Returns list of allowed models (`yolov8n.pt`, etc.) and default thresholds.
- [ ] **Automated Backend Tests**:
  ```bash
  python -m pytest backend/tests -v
  ```
  - Expected: 18 passed tests (API, Detector, Config, Session, WebSocket).

---

## 3. Frontend Dashboard Verification

- [ ] **Frontend Startup**:
  ```bash
  cd frontend
  npm run dev
  ```
  - Open `http://localhost:5173` in a modern browser (Chrome / Edge / Firefox).
- [ ] **Header & Connection Badge**:
  - Shows "Online" badge with green indicator dot when backend is running.
  - Displays current model badge (`yolov8n.pt`).
- [ ] **Automated Frontend Tests**:
  ```bash
  cd frontend
  npm test
  ```
  - Expected: 6 passed tests in Vitest.
- [ ] **Production Build**:
  ```bash
  cd frontend
  npm run build
  ```
  - Expected: Clean build with 0 TypeScript errors.

---

## 4. Live Camera & Object Detection Workflow

- [ ] **Camera Permission Request**:
  - Click **Start Detection**.
  - Browser displays camera permission dialog.
  - Grant permission: Video feed streams smoothly in the viewport.
- [ ] **Live Detection & Canvas Overlay**:
  - Hold common objects in view (person, smartphone, mug/cup, bottle, laptop, book).
  - Bounding boxes appear surrounding the objects with high accuracy.
  - Class label and percentage confidence pill badges render anchored to the top of each box.
- [ ] **Live Metrics Tracking**:
  - Frame rate displays live FPS (typically 20-30 FPS on modern CPUs).
  - Inference latency updates continuously (typically 15-40 ms for YOLOv8n).
  - Detected objects count dynamically matches number of detected boxes.
  - Session uptime timer counts up in `MM:SS` format.
- [ ] **Detection List (Sidebar)**:
  - Aggregate category tags display counts per class (e.g., `person (1)`, `cell phone (1)`).
  - List entries show class label, colored category dot, confidence progress bar, and pixel box coordinates.

---

## 5. Control State Transitions & Keyboard Accessibility

- [ ] **Pause Functionality**:
  - Click **Pause** button or press <kbd>Space</kbd>.
  - Overlay displays "Detection Paused".
  - Frame transmission stops; video view remains intact.
- [ ] **Resume Functionality**:
  - Click **Resume** button or press <kbd>Space</kbd>.
  - Detection immediately resumes without lag.
- [ ] **Stop Functionality**:
  - Click **Stop** button or press <kbd>S</kbd>.
  - Camera indicator light turns off.
  - Viewport returns to inactive placeholder state; metrics reset cleanly.

---

## 6. Dynamic Thresholds & Configuration

- [ ] **Confidence Slider**:
  - Drag Confidence Threshold slider between 5% and 100%.
  - Verify that low-confidence false positives disappear when slider is moved higher.
- [ ] **NMS / IoU Slider**:
  - Adjust IoU threshold slider.
  - Verify that overlapping duplicate boxes merge or separate as expected.
- [ ] **Settings Modal**:
  - Click Settings gear icon in the header.
  - Toggle "Display object class labels" and "Display confidence scores (%)".
  - Adjust bounding box thickness (1px to 4px).
  - Verify canvas updates immediately to reflect visual preferences.

---

## 7. Edge Cases & Resilience

- [ ] **WebSocket Disconnection & Auto-Reconnect**:
  - While detection is active, stop the backend (`Ctrl+C`).
  - Frontend immediately shows "Offline" badge and alert banner.
  - Restart backend: Frontend automatically reconnects via exponential backoff without requiring page refresh.
- [ ] **Camera Permission Denied**:
  - In browser site settings, block camera access.
  - Click Start Detection.
  - Clean error card appears explaining that camera permissions were blocked with a "Retry Camera Access" button.
- [ ] **IP Camera Stream Mode**:
  - Toggle source to "IP Camera / Stream".
  - Input a valid RTSP or HTTP video stream.
  - Start Detection to verify backend server capture.
  - Test an invalid URL to verify friendly error reporting.
