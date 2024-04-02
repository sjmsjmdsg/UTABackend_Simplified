import cv2
from uta.DataStructures._Data import _Data


class UIData(_Data):
    def __init__(self, screenshot_file, xml_file=None, resolution=(1080, 2280)):
        """
        Args:
            screenshot_file (path): .png or .jpg file path of the UI screenshot
            xml_file (path): .xml file path of the UI vh
            resolution (tuple): Specify the size/resolution of the UI
        """
        super().__init__()
        self.screenshot_file = screenshot_file
        self.xml_file = xml_file
        self.ui_id = screenshot_file.replace('/', '\\').split('\\')[-1].split('.')[0]

        # UI info
        self.ui_screenshot = cv2.resize(cv2.imread(screenshot_file), resolution)   # ui screenshot
        self.annotated_elements_screenshot = None
        self.annotated_elements_screenshot_path = None
        self.ui_vh_json = None      # ui vh json, after processing

        # UI elements
        self.elements_ids = 0       # count elements
        self.elements = []          # list of element in dictionary {'id':, 'class':...}
        self.elements_leaves = []   # leaf nodes that does not have children
        self.element_tree = None    # structural element tree, dict type
        self.blocks = []            # list of blocks from element tree
        self.ocr_text = []          # UI ocr detection result, list of __texts {}

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def show_each_element(self, only_leaves=False):
        """
        Show elements one by one
        Args:
            only_leaves (bool): True to just show element_leaves
        """
        board = self.ui_screenshot.copy()
        if only_leaves:
            elements = self.elements_leaves
            print(len(elements))
        else:
            elements = self.elements
        for ele in elements:
            print(ele['class'])
            print(ele, '\n')
            bounds = ele['bounds']
            clip = self.ui_screenshot[bounds[1]: bounds[3], bounds[0]: bounds[2]]
            color = (0, 255, 0) if not ele['clickable'] else (0, 0, 255)
            cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
            cv2.imshow('clip', cv2.resize(clip, (clip.shape[1] // 3, clip.shape[0] // 3)))
            cv2.imshow('ele', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
            if cv2.waitKey() == ord('q'):
                break
        cv2.destroyAllWindows()

    def show_all_elements(self, only_leaves=False):
        """
        Show all elements at once
        Args:
            only_leaves (bool): True to just show element_leaves
        """
        board = self.ui_screenshot.copy()
        if only_leaves:
            elements = self.elements_leaves
        else:
            elements = self.elements
        for ele in elements:
            bounds = ele['bounds']
            color = (0, 255, 0) if not ele['clickable'] else (0, 0, 255)
            cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
        cv2.imshow('elements', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('elements')

    def show_element_by_id(self, ele_id, show_children=True):
        """
        Show specific element by id
        Args:
            ele_id (int): id of element
            show_children (bool): True to show the children of the element
        """
        element = self.elements[ele_id]
        board = self.ui_screenshot.copy()
        color = (0, 255, 0) if not element['clickable'] else (0, 0, 255)
        bounds = element['bounds']
        cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), color, 3)
        if show_children and 'children-id' in element:
            for c_id in element['children-id']:
                bounds = self.elements[c_id]['bounds']
                cv2.rectangle(board, (bounds[0], bounds[1]), (bounds[2], bounds[3]), (255, 0, 255), 3)
        cv2.imshow('element', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('element')

    def show_screen(self):
        """
        Show screenshot of the UI
        """
        cv2.imshow('screen', self.ui_screenshot)
        cv2.waitKey()
        cv2.destroyWindow('screen')