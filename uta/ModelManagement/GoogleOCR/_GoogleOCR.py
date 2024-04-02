import requests
import json
from base64 import b64encode
import time
import cv2
from os.path import join as pjoin

from uta.DataStructures.Text import Text
from uta.config import *


class _GoogleOCR:
    def __init__(self):
        self.__url = 'https://vision.googleapis.com/v1/images:annotate'
        self.__api_key = open(WORK_PATH + 'uta/ModelManagement/GoogleOCR/googleapikey.txt', 'r').readline()

    @staticmethod
    def __make_image_data(img_path):
        """
        Prepares the image data for the API request.
        Args:
            img_path (str): Image file path.
        Returns:
            Encoded JSON data to be sent in the API request.
        """
        with open(img_path, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            # Setting up the request parameters for the OCR
            img_req = {
                'image': {
                    'content': ctxt
                },
                'features': [{
                    'type': 'DOCUMENT_TEXT_DETECTION',
                    # 'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }
        return json.dumps({"requests": img_req}).encode()

    @staticmethod
    def __text_cvt_orc_format(ocr_result):
        """
        Convert ocr result format for easier processing
        Args:
            ocr_result: [{'description': '5:08', 'boundingPoly': {'vertices': [{'x': 58, 'y': 16}, {'x': 113, 'y': 15},
             {'x': 113, 'y': 35}, {'x': 58, 'y': 36}]}}]
        Returns:
            __texts: [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        """
        texts = []
        if ocr_result is not None:
            for i, result in enumerate(ocr_result):
                error = False
                x_coordinates = []
                y_coordinates = []
                text_location = result['boundingPoly']['vertices']
                content = result['description']
                for loc in text_location:
                    if 'x' not in loc or 'y' not in loc:
                        error = True
                        break
                    x_coordinates.append(loc['x'])
                    y_coordinates.append(loc['y'])
                if error: continue
                location = {'left': min(x_coordinates), 'top': min(y_coordinates),
                            'right': max(x_coordinates), 'bottom': max(y_coordinates)}
                texts.append(Text(i, content, location))
        return texts

    @staticmethod
    def __merge_intersected_texts(texts):
        """
        Merge intersected __texts (sentences or words)
        """
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_intersected(text_b, bias=2):
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            texts = temp_set.copy()
        return texts

    @staticmethod
    def __text_filter_noise(texts):
        """
        Filter out some noise text that is abnormal single character
        """
        valid_texts = []
        for text in texts:
            if len(text.content) <= 1 and text.content.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&',
                                                                       '+']:
                continue
            valid_texts.append(text)
        return valid_texts

    @staticmethod
    def __text_sentences_recognition(texts):
        """
        Merge separate words detected by Google ocr into a sentence
        """
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_on_same_line(text_b, 'h', bias_justify=0.2 * min(text_a.height, text_b.height),
                                              bias_gap=1.3 * max(text_a.word_width, text_b.word_width)):
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            texts = temp_set.copy()
        for i, text in enumerate(texts):
            text.id = i
        return texts

    @staticmethod
    def __resize_label(texts, shrink_rate):
        """
        Resize the labels of text by certain ratio
        Args:
            shrink_rate: rate to resize
        """
        for text in texts:
            for key in text.location:
                text.location[key] = round(text.location[key] / shrink_rate)
        return texts

    @staticmethod
    def __wrap_up_texts(texts):
        """
        Wrap up Text objects to list of dicts
        Args:
            texts (list of _Text)
        Returns:
            texts_dict (list of dict): [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        """
        texts_dict = []
        for i, text in enumerate(texts):
            loc = text.location
            t = {'id': i,
                 'bounds': [loc['left'], loc['top'], loc['right'], loc['bottom']],
                 'content': text.content}
            texts_dict.append(t)
        return texts_dict

    @staticmethod
    def visualize_texts(texts, img, shown_resize_height=800, show=False, write_path=None):
        """
        Visualize the __texts
        Args:
            texts (list): List of Text
            img (cv2 img): original image to draw on
            shown_resize_height: The height of the shown image for better view
            show (bool): True to show on popup window
            write_path (sting): Path to save the visualized image, None for not saving
        Returns:

        """
        for text in texts:
            text.visualize_element(img, line=2)
        img_resize = img
        if shown_resize_height is not None:
            img_resize = cv2.resize(img, (int(shown_resize_height * (img.shape[1] / img.shape[0])),
                                          shown_resize_height))

        if show:
            cv2.imshow('__texts', img_resize)
            cv2.waitKey(0)
            cv2.destroyWindow('__texts')
        if write_path is not None:
            cv2.imwrite(write_path, img_resize)
        return img_resize

    @staticmethod
    def save_detection_json(texts, img_shape, file_path):
        """
        Save the Text to local as json file
        Args:
            texts (list): list of Text
            img_shape (tuple): image size
            file_path: File to save
        """
        f_out = open(file_path, 'w')
        output = {'img_shape': img_shape, '__texts': []}
        for text in texts:
            c = {'id': text.id, 'content': text.content}
            loc = text.location
            c['column_min'], c['row_min'], c['column_max'], c['row_max'] = loc['left'], loc['top'], loc['right'], loc['bottom']
            c['width'] = text.width
            c['height'] = text.height
            output['__texts'].append(c)
        json.dump(output, f_out, indent=4)

    def request_google_ocr(self, img_path):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            img_path (str): Image file path.
        Returns:
            The detected text annotations or None if no text is found.
        """
        try:
            img_data = self.__make_image_data(img_path)  # Prepare the image data

            # Post request to the Google Cloud Vision API
            response = requests.post(self.__url, data=img_data, params={'key': self.__api_key},
                                     headers={'Content_Type': 'application/json'})

            # Handling the API response
            if 'responses' not in response.json():
                raise Exception(response.json())
            if response.json()['responses'] == [{}]:
                return None  # Return None if no text is detected
            else:
                return response.json()['responses'][0]['textAnnotations'][1:]
        except Exception as e:
            raise e

    def detect_text_ocr(self, img_path, output_dir='data/output', show=False, shrink_size=False):
        """
        Detect __texts on the image using google ocr
        Args:
            img_path: The file path of the image
            output_dir: Directory to store the output
            show (bool): True to visualize the result
            shrink_size (bool): True to shrink the image before processing for faster speed
        Returns:
            __texts (list of dicts): [{'id': 0, 'bounds': [77, 20, 151, 48], 'content': '5:08'}]
        """
        start = time.time()
        name = img_path.replace('\\', '/').split('/')[-1][:-4]
        org_img = cv2.imread(img_path)
        if shrink_size:
            shrink_rate = 0.75
            img_re = cv2.resize(org_img, (int(org_img.shape[1] * shrink_rate),
                                          int(org_img.shape[0] * shrink_rate)))
            img_path = img_path[:-4] + '_resize.jpg'
            cv2.imwrite(img_path, img_re)

        ocr_result = self.request_google_ocr(img_path)
        texts = self.__text_cvt_orc_format(ocr_result)
        texts = self.__merge_intersected_texts(texts)
        texts = self.__text_filter_noise(texts)
        texts = self.__text_sentences_recognition(texts)
        if shrink_size:
            texts = self.__resize_label(texts, shrink_rate)
        if show:
            self.visualize_texts(texts=texts, img=org_img, show=True)
            print("[Text Detection Completed in %.3f s] Input: %s Output: %s"
                  % (time.time() - start, img_path, pjoin(output_dir, name + '.json')))
        return self.__wrap_up_texts(texts)


if __name__ == '__main__':
    google = _GoogleOCR()
    google.detect_text_ocr(img_path=WORK_PATH + '/data/user1/task1/0.png', output_dir=WORK_PATH + '/data/ocr',
                           shrink_size=True, show=True)
