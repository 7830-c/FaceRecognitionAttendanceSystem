import os
import pathlib

CURRENT_FILE_DIR = pathlib.Path(__file__).parent  #Util dir path
PROJECT_ROOT = CURRENT_FILE_DIR.parent #project root



DATABASE_FILEPATH = os.path.join(str(PROJECT_ROOT), "Data", "University.db")
Student_IMG_DIR=os.path.join(str(PROJECT_ROOT),"Data","StudentImages")
encodingFileName=os.path.join(str(PROJECT_ROOT),"Data","encodings.p")
