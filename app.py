from fastapi import FastAPI, File, UploadFile, HTTPException
import cv2
import dlib
import numpy as np
import base64
from fastapi.responses import JSONResponse

app = FastAPI()
print("Server is UP")
# Load Dlib's pre-trained models
try:
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
except Exception as e:
    raise RuntimeError(f"Error loading models: {e}")


def is_image_blurry(image, threshold=100):
    """Check if the image is blurry using the variance of the Laplacian."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var < threshold
    except Exception as e:
        raise RuntimeError(f"Error in blur detection: {e}")


def is_image_too_bright_or_dark(image, bright_threshold=220, dark_threshold=30):
    """Check if the image is too bright or too dark based on average pixel intensity."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        return mean_brightness > bright_threshold or mean_brightness < dark_threshold
    except Exception as e:
        raise RuntimeError(f"Error in brightness detection: {e}")


def image_to_base64(image):
    """Convert an image to base64 encoded string."""
    try:
        _, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)
        return jpg_as_text.decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"Error in image encoding: {e}")


@app.post("/process_image/")
async def process_image(file: UploadFile = File(...)):
    try:
        # Reading the uploaded file
        file_bytes = await file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(
                status_code=400, detail="Invalid image format.")

        # Check for blurriness or poor lighting
        if is_image_blurry(image):
            raise HTTPException(
                status_code=400, detail="Image is too blurry. Please upload a clear image.")

        if is_image_too_bright_or_dark(image):
            raise HTTPException(
                status_code=400, detail="Image has poor lighting. Ensure proper lighting conditions.")

        # Detect faces
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        if not faces:
            raise HTTPException(
                status_code=400, detail="No faces detected. Please upload an image with a visible face.")

        # Draw landmarks on the detected face(s)
        for face in faces:
            landmarks = predictor(gray, face)
            for i in range(68):
                x, y = landmarks.part(i).x, landmarks.part(i).y
                cv2.circle(image, (x, y), 3, (255, 255, 255), -1)

        # Save and convert the processed image to base64
        preview = image_to_base64(image)

        return {"message": "Image processed successfully with landmarks detected.", "preview": preview}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}")
