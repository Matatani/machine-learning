from ultralytics import YOLO
import cv2

class PaddyPredictor():
    def __init__(self):
        self.model = YOLO("./predictor/yolo11x-seg_best.pt")

    def predict_image(self, image_path, output_path):
        image_array = cv2.imread(image_path)
        result = self.model(image_array)
        r = result[0]
        img = r.plot()
        cv2.imwrite(output_path, img)
