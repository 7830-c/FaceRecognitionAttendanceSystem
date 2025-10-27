
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "Data"
STUDENT_IMG_DIR = DATA_DIR / "StudentImages"
ENCODING_FILE_NAME = DATA_DIR / "encodings.p"
DATABASE_FILEPATH = DATA_DIR / "University.db"

STUDENT_IMG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

if __name__=="__main__":
    print(f"BASE_DIR = {BASE_DIR}")
    print(f"STUDENT_IMG_DIR = {STUDENT_IMG_DIR}")
    print(f"ENCODING_FILE_NAME  = {ENCODING_FILE_NAME }")













