import joblib
import cv2
import os
import numpy as np

def applyClahe(image, clip_limit=2.0, tile_grid_size=(8,8)):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    clahe = cv2.createCLAHE(clip_limit, tile_grid_size)
    hsv_image[:,:,2] = clahe.apply(hsv_image[:,:,2])
    return cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

def resize_image(image, size=(150, 150)):
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)

def blur_image(image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(image, kernel_size, 0)

def process_image(args):
    image_path, preprocessing_methods = args
    image = cv2.imread(image_path)
    for method in preprocessing_methods:
        image = method(image)

    label = os.path.basename(os.path.dirname(image_path))
    return image, label

def extract_histogram_features(images, hist_bins=16):
    all_features = []

    for i, image in enumerate(images):
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        h_hist = cv2.calcHist([hsv_image], [0], None, [hist_bins], [0, 180])
        s_hist = cv2.calcHist([hsv_image], [1], None, [hist_bins], [0, 256])
        v_hist = cv2.calcHist([hsv_image], [2], None, [hist_bins], [0, 256])

        h_hist = cv2.normalize(h_hist, h_hist).flatten()
        s_hist = cv2.normalize(s_hist, s_hist).flatten()
        v_hist = cv2.normalize(v_hist, v_hist).flatten()

        features.extend(h_hist)
        features.extend(s_hist)
        features.extend(v_hist)

        all_features.append(features)

    return np.array(all_features)

class PaddyPredictor():
    def __init__(self):
        # Load trained model and scaler
        self.model = joblib.load("./predictor/model.pkl")
        self.scaler = joblib.load("./predictor/scaler.pkl")
        self.preprocess_methods = [resize_image, blur_image, applyClahe]

    def predict_image(self, image_path):
        image, _ = process_image((image_path, self.preprocess_methods))
        features = extract_histogram_features([image])
        features_normalized = self.scaler.transform(features)
        predicted_label = self.model.predict(features_normalized)[0]
        return predicted_label