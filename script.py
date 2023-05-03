import sys
import cv2
from PIL import Image, ImageDraw


def detect_faces_and_eyes(image):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adjust these parameters to improve face detection
    scaleFactor = 1.1
    minNeighbors = 5
    faces = face_cascade.detectMultiScale(gray, scaleFactor, minNeighbors)

    eyes_coordinates = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]

        # Adjust these parameters to improve eye detection
        scaleFactor = 1.1
        minNeighbors = 5
        minSize = (30, 30)
        maxSize = (60, 60)
        eyes = eye_cascade.detectMultiScale(
            roi_gray, scaleFactor, minNeighbors, 0, minSize, maxSize)

        for (ex, ey, ew, eh) in eyes:
            eyes_coordinates.append((x+ex, y+ey, ew, eh))

    return eyes_coordinates


def add_censor_bar(image, eyes_coordinates):
    draw = ImageDraw.Draw(image)
    bar_height = 10

    # Get the minimum and maximum x, y coordinates for all detected eyes
    x_values = [x for x, y, w, h in eyes_coordinates]
    y_values = [y for x, y, w, h in eyes_coordinates]
    min_x = min(x_values)
    max_x = max([x + w for x, y, w, h in eyes_coordinates])
    min_y = min(y_values)
    max_y = max([y + h for x, y, w, h in eyes_coordinates])

    # Extend the width of the censor bar to cover most of the face
    face_width = max_x - min_x
    face_margin = face_width // 5
    censor_bar_left = max(min_x - face_margin, 0)
    censor_bar_top = min_y - bar_height // 2
    censor_bar_right = min(max_x + face_margin, image.size[0])
    censor_bar_bottom = max_y + bar_height // 2

    draw.rectangle([(censor_bar_left, censor_bar_top),
                    (censor_bar_right, censor_bar_bottom)], fill="red")
    print(f"Censor bar added at ({censor_bar_left},{censor_bar_top})")

    return image


def main(image_path):
    # Read the input image using OpenCV
    cv_image = cv2.imread(image_path)

    # Detect faces and eyes
    eyes_coordinates = detect_faces_and_eyes(cv_image)
    print(f"Detected {len(eyes_coordinates)} eyes")

    if not eyes_coordinates:
        print("No eyes detected")
        sys.exit(1)

    # Convert the OpenCV image to a PIL image
    pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

    # Add censor bars
    censored_image = add_censor_bar(pil_image, eyes_coordinates)

    # Save the output image
    censored_image.save("output.jpg")
    print("Output image saved as output.jpg")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"Processing image: {image_path}")
    main(image_path)
