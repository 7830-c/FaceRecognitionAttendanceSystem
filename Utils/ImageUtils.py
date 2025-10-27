import cv2
import face_recognition
import numpy as np
import os
import pickle

from Utils.Paths import Student_IMG_DIR,encodingFileName

def saveImage(img,idNo,name):
    os.makedirs("Data", exist_ok=True)
    img_path_name = os.path.join(Student_IMG_DIR, f"{idNo}_{name}.png")
    img_bytes = np.frombuffer(img.read(), np.uint8)  # convert image bytes to numpy bytes data
    img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)  # decode to open cv colored image
    cv2.imwrite(img_path_name, img)
    print("Img saved")
    return img_path_name


def generateEncodings(img_path, enrollNo, Name):

    enrollNo = str(enrollNo)
    ids, names, Image_encodings = [], [], []
    if os.path.exists(encodingFileName):
        try:
            with open(encodingFileName, "rb") as f:
                encodings = pickle.load(f)
                ids, names, Image_encodings = encodings
        except (EOFError, FileNotFoundError): # Handles empty or non-existent file
            print(f"Warning: Encoding file '{encodingFileName}' is empty or corrupt. Starting fresh.")

    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read image at path: {img_path}")
        return 0

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)

    if len(face_locations) == 0:  # No face detected
        os.remove(img_path)
        print("Error: No face detected in the image.")
        return 0

    elif len(face_locations) > 1:  # Multiple faces detected
        os.remove(img_path)
        print("Error: Multiple faces detected in the image.")
        return 2

    new_encoding = face_recognition.face_encodings(img, face_locations)[0]

    #remove old record.If exist
    if enrollNo in ids:
        index = ids.index(enrollNo)
        del names[index]
        del ids[index]
        del Image_encodings[index]

        print(f"Update: Removed previous encoding for Enrollment No. {enrollNo}.")

    Image_encodings.append(new_encoding)
    ids.append(enrollNo)
    names.append(Name)

    newEncodedData = [ids, names, Image_encodings]
    try:
        with open(encodingFileName, "wb") as f:
            pickle.dump(newEncodedData, f)

        print(f"Success: Details {'updated' if 'Update' in locals() else 'added'} and file saved.")
        return 1
    except Exception as e:
        print(f"Critical Error: Failed to save encoding file. {e}")
        return 0


def removeEncoding(enrollNo):
    enrollNo = str(enrollNo)
    if os.path.exists(encodingFileName):
        try:
            with open(encodingFileName, "rb") as f:
                encodings = pickle.load(f)
            ids, names, Image_encodings = encodings
        except EOFError:
            print(f"Warning: Encoding file '{encodingFileName}' is empty or corrupted. Initializing empty lists.")
            ids, names, Image_encodings = [], [], []
    else:
        print(f"File '{encodingFileName}' does not exist. No encodings to remove.")
        return

    if enrollNo in ids:
        try:
            index = ids.index(enrollNo)
            names.remove(names[index])
            ids.remove(enrollNo)
            del Image_encodings[index]
            print(f"Successfully removed encoding for Enrollment No: {enrollNo}")
        except ValueError:
            print(f"Error: Could not find Enrollment No. {enrollNo} in the 'ids' list.")
            return

    else:
        print(f"Enrollment No. {enrollNo} not found in the database. No removal performed.")
        return

    newEncodedData = [ids, names, Image_encodings]

    try:
        with open(encodingFileName, "wb") as f:
            pickle.dump(newEncodedData, f)
        print("Encoding file updated successfully.")
    except Exception as e:
        print(f"Error saving updated encoding file: {e}")




