import os
import subprocess
import uuid
import shutil
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TEMPLATE_FILE = "template (1).scad"
TEMP_DIR = Path("temp_renders")
TEMP_DIR.mkdir(exist_ok=True)

# Anchors for string replacement in the .scad file
ANCHOR_1 = 'String1 = "DUAL WORD"'
ANCHOR_2 = 'String2 = "ILLUSION"'

def sanitize_input(text: str) -> str:
    """Remove characters that could be used for SCAD injection."""
    return "".join(c for c in text if c.isalnum() or c == " ")

@app.get("/render")
async def render_scad(
    name1: str = Query(..., max_length=10),
    name2: str = Query(..., max_length=10),
    color: str = Query("#ffffff")
):
    # 1. Sanitize and prepare names
    n1 = sanitize_input(name1).upper()
    n2 = sanitize_input(name2).upper()

    if not n1 or not n2:
        raise HTTPException(status_code=400, detail="Names cannot be empty")

    # 2. Generate unique IDs for this request to avoid collisions
    request_id = str(uuid.uuid4())
    scad_path = TEMP_DIR / f"{request_id}.scad"
    stl_path = TEMP_DIR / f"{request_id}.stl"

    try:
        # 3. Read template and inject parameters
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace(ANCHOR_1, f'String1 = "{n1}"')
        content = content.replace(ANCHOR_2, f'String2 = "{n2}"')

        with open(scad_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 4. Execute OpenSCAD CLI
        # We use --export-format stl to generate the mesh
        # Note: openscad must be in the system PATH
        try:
            subprocess.run(
                ["openscad", "-o", str(stl_path), str(scad_path)],
                check=True,
                capture_output=True,
                timeout=15
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"OpenSCAD error: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="OpenSCAD render timeout")

        # 5. Return the file and schedule deletion
        return FileResponse(
            stl_path,
            media_type="model/stl+facet",
            filename="preview.stl"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Note: In a production environment, use a background task or
        # periodic cleanup to remove files from TEMP_DIR.
        # For this MVP, we'll leave the files and suggest a cleanup script.
        pass

@app.get("/cleanup")
async def cleanup():
    """Utility to clear the temp folder"""
    for file in TEMP_DIR.glob("*"):
        file.unlink()
    return {"status": "cleaned"}

# Serve static files from the website directory
app.mount("/", StaticFiles(directory="website", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
