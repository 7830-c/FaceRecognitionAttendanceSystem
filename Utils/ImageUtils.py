import cv2
import face_recognition
import numpy as np
import os
import pickle

from Utils.Paths import STUDENT_IMG_DIR, BASE_DIR, ENCODING_FILE_NAME


def saveImage(img, idNo, name):

    os.makedirs(STUDENT_IMG_DIR, exist_ok=True)  

    safe_name = str(name).strip().replace(" ", "_")
    relative_path = os.path.join("Data", "StudentImages", f"{idNo}_{safe_name}.png")
    absolute_path = os.path.normpath(os.path.join(BASE_DIR, relative_path))

    try:
        img_bytes = np.frombuffer(img.read(), np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Uploaded file is not a valid image")

        cv2.imwrite(absolute_path, img)
        print(f"Image saved successfully at: {absolute_path}")
        return relative_path

    except Exception as e:
        print(f"Error while saving image: {e}")
        return None



def get_absolute_path(relative_path):
    return os.path.normpath(os.path.join(BASE_DIR, relative_path))


def generateEncodings(img_path, enrollNo, Name):
    enrollNo = str(enrollNo)
    ids, names, Image_encodings = [], [], []

    if os.path.exists(encodingFileName):
        try:
            with open(encodingFileName, "rb") as f:
                ids, names, Image_encodings = pickle.load(f)
        except (EOFError, FileNotFoundError, pickle.UnpicklingError):
            print(f"Encoding file '{encodingFileName}' is empty or corrupt. Starting fresh.")

    img_abs_path = get_absolute_path(img_path)
    img = cv2.imread(img_abs_path)

    if img is None:
        print(f"Error: Could not read image at path: {img_abs_path}")
        return 0

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)

    
    if len(face_locations) == 0:
        os.remove(img_abs_path)
        print("No face detected in the image.")
        return 0
    elif len(face_locations) > 1:
        os.remove(img_abs_path)
        print("Multiple faces detected in the image.")
        return 2

    new_encoding = face_recognition.face_encodings(img, face_locations)[0]

    # Remove old record if exists
    if enrollNo in ids:
        index = ids.index(enrollNo)
        del names[index]
        del ids[index]
        del Image_encodings[index]
        print(f"Old encoding removed for Enrollment No: {enrollNo}")

    # Add new encoding
    ids.append(enrollNo)
    names.append(Name)
    Image_encodings.append(new_encoding)

    try:
        with open(encodingFileName, "wb") as f:
            pickle.dump([ids, names, Image_encodings], f)
        print("Encoding file saved successfully.")
        return 1
    except Exception as e:
        print(f"Critical Error: Failed to save encoding file: {e}")
        return 0



def removeEncoding(enrollNo):
    enrollNo = str(enrollNo)

    if not os.path.exists(encodingFileName):
        print(f"Encoding file '{encodingFileName}' not found. Nothing to remove.")
        return

    try:
        with open(encodingFileName, "rb") as f:
            ids, names, Image_encodings = pickle.load(f)
    except Exception as e:
        print(f"Error reading encoding file: {e}")
        return

    if enrollNo not in ids:
        print(f"Enrollment No. {enrollNo} not found in the encoding list.")
        return

    try:
        index = ids.index(enrollNo)
        del ids[index]
        del names[index]
        del Image_encodings[index]

        with open(encodingFileName, "wb") as f:
            pickle.dump([ids, names, Image_encodings], f)

        print(f"Successfully removed encoding for Enrollment No: {enrollNo}")
    except Exception as e:
        print(f"Error updating encoding file: {e}")
