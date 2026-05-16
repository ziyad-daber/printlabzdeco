# Testing Guide: PrintLabz 3D Preview Pipeline

This document describes how to set up, run, and verify the real-time 3D rendering pipeline.

## 🛠 Prerequisites

Before testing, ensure the following are installed on your system:

1. **OpenSCAD**: The backend relies on the OpenSCAD CLI.
   - [Download OpenSCAD](https://openscad.org/downloads.html)
   - **CRITICAL**: The `openscad` executable must be in your system **PATH**. 
   - *Verification*: Open a terminal and run `openscad -v`. If it's not recognized, add the installation folder to your environment variables.

2. **Python Dependencies**:
   - Install FastAPI and Uvicorn:
     ```bash
     pip install fastapi uvicorn
     ```

## 🚀 How to Run

### 1. Start the Backend
The backend handles the SCAD-to-STL conversion.
```bash
python server.py
```
- The server should start at `http://0.0.0.0:8000`.
- Keep this terminal open.

### 2. Launch the Frontend
Open `website/index.html` in a modern web browser (Chrome, Firefox, or Edge).
- *Note*: You can simply double-click the file, or use a VS Code "Live Server" extension.

---

## 🧪 Test Cases

### Case 1: The "Golden Path" (Basic Functionality)
1. Enter a name in **Prénom 1** (e.g., "SARA").
2. Enter a name in **Prénom 2** (e.g., "KARIM").
3. **Expected Result**: 
   - The "Generating 3D..." loader appears.
   - After a brief delay, a 3D mesh appears in the canvas.
   - Drag the mouse/finger to rotate the object and verify the "Illusion" effect (different names from different angles).

### Case 2: Real-time Updates & Debouncing
1. Type rapidly into the input fields.
2. **Expected Result**: 
   - The 3D model should not update on *every* single keystroke (this prevents server crashing).
   - It should update $\sim$500ms after you stop typing.

### Case 3: Gallery Prefills
1. Click on one of the example items in the **Showroom** (e.g., "SARA × ADAM").
2. **Expected Result**: 
   - The input fields are automatically filled.
   - The page scrolls to the 3D canvas.
   - The 3D preview updates to match the prefilled names.

### Case 4: Color Synchronization
1. Select a different color from the swatches.
2. **Expected Result**: 
   - The 3D model's material should smoothly transition to the selected color.

### Case 5: Input Sanitization (Security)
1. Try entering special characters or symbols (e.g., `SARAH! @#`).
2. **Expected Result**: 
   - The frontend/backend should sanitize the input.
   - The 3D render should still succeed using only alphanumeric characters.

---

## 🔍 Troubleshooting

| Issue | Potential Cause | Solution |
| :--- | :--- | :--- |
| **"Error rendering 3D"** in browser | Backend is not running or OpenSCAD is missing. | Check if `server.py` is running and `openscad -v` works in terminal. |
| **Canvas is empty** | CORS error or blocked request. | Ensure the server is running on port 8000 and browser console has no red errors. |
| **Slow Rendering** | OpenSCAD is taking too long. | Check the `server.py` logs. The timeout is set to 15s. |
| **Files piling up** | Temp files not being deleted. | Run `http://localhost:8000/cleanup` in the browser to clear the `temp_renders` folder. |
