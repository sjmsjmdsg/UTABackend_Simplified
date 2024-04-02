import cv2
import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms
import json
from PIL import Image
from uta.config import *


class _IconClassifier:
    def __init__(self, model_path=WORK_PATH + 'uta/ModelManagement/VisionModel/icon_classifier_model_results/best-0.93.pt',
                 class_path=WORK_PATH + 'uta/ModelManagement/VisionModel/icon_classifier_model_results/iconModel_labels.json'):
        # Setting the device to GPU if available, else CPU
        self.__device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # Transformations to apply on the input images
        self.__transform_test = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

        # Load the trained model
        # s = time.time()
        self.__model = torch.load(model_path, map_location=self.__device).to(self.__device)
        self.__class_names = json.load(open(class_path, "r"))
        # print("Load Classifier Model: %.3fs" % (time.time() - s))

    def classify_icons(self, imgs):
        """
        Predict the class of the given icons images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        try:
            # convert cv2 image to PIL image
            if type(imgs[0]) == np.ndarray:
                imgs = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in imgs if len(img) > 0]

            # Apply transformations and convert to batch tensor
            inputs = [self.__transform_test(img) for img in imgs]
            inputs = torch.stack(inputs).to(self.__device)

            # forward
            with torch.set_grad_enabled(False):
                outputs = self.__model(inputs)
                outputs = nn.Softmax(dim=1)(outputs)
                values, preds = torch.max(outputs, 1)

            # Collect results with confidence score
            results = []
            for j in range(inputs.size()[0]):
                poss = values[j].item()
                if poss > 0.8:
                    results.append([self.__class_names[preds[j]], poss])
                else:
                    results.append(["other", poss])
            return results
        except Exception as e:
            raise e
