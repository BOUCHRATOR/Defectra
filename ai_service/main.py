def main():
    print("Hello from ai-service!")


if __name__ == "__main__":
    main()


# ==========================================================
# main.py
# ==========================================================

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.defect import router as defect_router
from api.chat import router as chat_router
from api.qa import router as qa_router
from api.upload import router as upload_router
from api.report import router as report_router
from api.live import router as live_router
from api.voice import router as voice_router
from api.voice_qa import router as voice_qa_router
# ==========================================================
# APPLICATION
# ==========================================================

app = FastAPI(
    title="Defectra AI Service",
    version="1.0.0"
)
app.include_router(chat_router)
app.include_router(qa_router)
app.include_router(upload_router)
app.include_router(report_router)
app.include_router(live_router)
app.include_router(voice_router)
app.include_router(voice_qa_router)
app.include_router(defect_router)

# ==========================================================
# CHEMINS
# ==========================================================

# Dossier :
# C:\Users\LENOVO\Downloads\Data_vechule\ai_service

BASE_DIR = Path(__file__).resolve().parent

# Dossier :
# C:\Users\LENOVO\Downloads\Data_vechule

PROJECT_DIR = BASE_DIR.parent

# Dossier Django :
# C:\Users\LENOVO\Downloads\Data_vechule\backend

BACKEND_DIR = PROJECT_DIR / "backend"

# Dossier media :
# C:\Users\LENOVO\Downloads\Data_vechule\backend\media

BACKEND_MEDIA_DIR = BACKEND_DIR / "media"

# Dossier inspections :
# C:\Users\LENOVO\Downloads\Data_vechule\backend\media\inspections

INSPECTIONS_DIR = BACKEND_MEDIA_DIR / "inspections"


# ==========================================================
# CREATION DES DOSSIERS
# ==========================================================

BACKEND_MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

INSPECTIONS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# DEBUG CHEMINS
# ==========================================================

print()
print("========================================")
print("CHEMINS MEDIA")
print("========================================")
print("BASE_DIR :")
print(BASE_DIR)
print()
print("PROJECT_DIR :")
print(PROJECT_DIR)
print()
print("BACKEND_DIR :")
print(BACKEND_DIR)
print()
print("BACKEND_MEDIA_DIR :")
print(BACKEND_MEDIA_DIR)
print()
print("INSPECTIONS_DIR :")
print(INSPECTIONS_DIR)
print()
print("MEDIA EXISTE :", BACKEND_MEDIA_DIR.exists())
print("INSPECTIONS EXISTE :", INSPECTIONS_DIR.exists())
print("========================================")
print()


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# FICHIERS MEDIA
# ==========================================================

app.mount(
    "/media",
    StaticFiles(
        directory=str(BACKEND_MEDIA_DIR)
    ),
    name="media"
)


# ==========================================================
# ROUTERS
# ==========================================================

from api.defect import router as defect_router




# ==========================================================
# ROUTE TEST
# ==========================================================

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Defectra AI Service fonctionne.",
        "media_directory": str(BACKEND_MEDIA_DIR),
        "media_exists": BACKEND_MEDIA_DIR.exists()
    }


# ==========================================================
# TEST MEDIA
# ==========================================================

@app.get("/media-test")
def media_test():

    files = []

    if INSPECTIONS_DIR.exists():

        for file in INSPECTIONS_DIR.iterdir():

            if file.is_file():

                files.append(file.name)

    return {
        "media_directory": str(BACKEND_MEDIA_DIR),
        "inspections_directory": str(INSPECTIONS_DIR),
        "files": files
    }