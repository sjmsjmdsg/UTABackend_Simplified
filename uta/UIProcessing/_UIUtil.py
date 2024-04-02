from difflib import SequenceMatcher
import cv2
import numpy as np


class _UIUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_ui_element_node_by_id(ui_data, ele_id):
        """
        Return UI element by its id
        Args:
            ui_data (UIData): Target UIData
            ele_id (str or int): The element ID
        Returns:
            Element node (dict): If found, otherwise None
        """
        def search_node_by_id(node, ele_id):
            '''
            Recursively search for node by element id, if not matched for current node, look into its children
            '''
            if node['id'] == ele_id:
                return node
            if node['id'] > ele_id:
                return None
            if 'children' in node:
                last_child = None
                for child in node['children']:
                    if child['id'] == ele_id:
                        return child
                    if child['id'] > ele_id:
                        break
                    last_child = child
                return search_node_by_id(last_child, ele_id)

        ele_id = int(ele_id)
        if ele_id >= len(ui_data.elements):
            print('No element with id', ele_id, 'is found')
            return None
        return search_node_by_id(ui_data.element_tree, ele_id)

    @staticmethod
    def check_ui_tree_similarity(ui_data1, ui_data2):
        """
        Compute the similarity between two uis by checking their element trees
        Args:
            ui_data1 (UIData): The comparing ui
            ui_data2 (UIData): The comparing ui
        Returns:
            similarity (float): The similarity between two trees
        """
        return SequenceMatcher(None, str(ui_data1.element_tree), str(ui_data2.element_tree)).ratio()

    def annotate_elements_with_id(self, ui_data, only_leaves=True, show=True, draw_bound=False):
        """
        Annotate elements on the ui screenshot using IDs
        Args:
            ui_data (UIData): Target UIData
            only_leaves (bool): True to just show element_leaves
            show (bool): True to show the result
            draw_bound (bool): True to draw bounding box of elements
        Returns:
            annotated_img (cv2 image): Annotated UI screenshot
        """
        board = ui_data.ui_screenshot.copy()
        if only_leaves:
            elements = ui_data.elements_leaves
        else:
            elements = ui_data.elements
        # draw bounding box
        if draw_bound:
            for ele in elements:
                left, top, right, bottom = ele['bounds']
                cv2.rectangle(board, (left, top), (right, bottom), (0, 250, 0), 2)
                board = self.draw_transparent_border_rectangle(board, (left, top), (right, bottom), (0, 250, 0), 3, 0.7)
        # annotate elements
        for i, ele in enumerate(elements):
            left, top, right, bottom = ele['bounds']
            try:
                # mark on the top if possible
                board = self.putBText(board, str(ele['id']), text_offset_x=(left + right) // 2, text_offset_y=top - 5,
                                      vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=(10,10,10),
                                      text_RGB=(200,200,200), alpha=0.55)
            except ValueError as e:
                # else mark on the bottom
                board = self.putBText(board, str(ele['id']), text_offset_x=(left + right) // 2, text_offset_y=bottom,
                                      vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=(10,10,10),
                                      text_RGB=(200,200,200), alpha=0.55)
        if show:
            cv2.imshow('a', cv2.resize(board, (500, 1000)))
            cv2.waitKey()
            cv2.destroyAllWindows()
        return board

    '''
    ***************
    *** Drawing ***
    ***************
    '''
    @staticmethod
    def putBText(img, text, text_offset_x=20, text_offset_y=20, vspace=10, hspace=10, font_scale=1.0, background_RGB=(228, 225, 222), text_RGB=(1, 1, 1), font=cv2.FONT_HERSHEY_DUPLEX, thickness=2, alpha=0.6, gamma=0):
        """
        Inputs:
            img: cv2 image img
            text_offset_x, text_offset_x: X,Y location of text start
            vspace, hspace: Vertical and Horizontal space between text and box boundries
            font_scale: Font size
            background_RGB: Background R,G,B color
            text_RGB: Text R,G,B color
            font: Font Style e.g. cv2.FONT_HERSHEY_DUPLEX,cv2.FONT_HERSHEY_SIMPLEX,cv2.FONT_HERSHEY_PLAIN,cv2.FONT_HERSHEY_COMPLEX
                  cv2.FONT_HERSHEY_TRIPLEX, etc
            thickness: Thickness of the text font
            alpha: Opacity 0~1 of the box around text
            gamma: 0 by default
        Output:
            img: CV2 image with text and background
        """
        R, G, B = background_RGB[0], background_RGB[1], background_RGB[2]
        text_R, text_G, text_B = text_RGB[0], text_RGB[1], text_RGB[2]
        (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=thickness)[0]
        x, y, w, h = text_offset_x, text_offset_y, text_width, text_height
        crop = img[y - vspace:y + h + vspace, x - hspace:x + w + hspace]
        white_rect = np.ones(crop.shape, dtype=np.uint8)
        b, g, r = cv2.split(white_rect)
        rect_changed = cv2.merge((B * b, G * g, R * r))

        res = cv2.addWeighted(crop, alpha, rect_changed, 1 - alpha, gamma)
        img[y - vspace:y + vspace + h, x - hspace:x + w + hspace] = res

        cv2.putText(img, text, (x, (y + h)), font, fontScale=font_scale, color=(text_B, text_G, text_R), thickness=thickness)
        return img

    @staticmethod
    def draw_transparent_border_rectangle(img, left_top, right_bottom, color, thickness, alpha):
        overlay = np.zeros_like(img, dtype=np.uint8)
        cv2.rectangle(overlay, left_top, right_bottom, color, thickness)
        return cv2.addWeighted(overlay, alpha, img, 1, 0)

