from uta.config import *
from uta.UIProcessing._UIPreProcessor import _UIPreProcessor
from uta.UIProcessing._UIAnalyser import _UIAnalyser
from uta.UIProcessing._UIChecker import _UIChecker
from uta.UIProcessing._UIUtil import _UIUtil


class UIProcessor:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        self.__ui_preprocessor = _UIPreProcessor()
        self.__ui_analyser = _UIAnalyser(self.__model_manager)
        self.__ui_checker = _UIChecker(self.__model_manager)
        self.__ui_util = _UIUtil()

    '''
    ***********************
    *** Process UI Info ***
    ***********************
    '''
    def process_ui(self, ui_data, show=False, ocr=True, cls=False):
        """
        Process a UI, including
            1. Pre-process UI
            2. Analyze UI
        Args:
            ui_data (UIData): UI data before processing
            show (bool): True to show processing result on window
            ocr (bool): True to turn on ocr for the whole UI image
            cls (bool): True to turn on UI element classification
        Returns:
            ui_data (UIData): UI data after processing
        """
        self.preprocess_ui(ui_data)
        self.analyze_ui(ui_data, ocr=ocr, cls=cls)
        if show:
            ui_data.show_all_elements()
        return ui_data

    def preprocess_ui(self, ui_data):
        """
        Process a UI, including
            1. Convert vh to tidy and formatted json
            2. Extract basic UI info (elements) and store as dicts
            3. Build element tree
        Args:
            ui_data (UIData): ui data for processing
        Returns:
            ui_data.ui_vh_json (dict): VH in a tidy json format
            ui_data.elements; ui_data.elements_leaves (list of dicts)
            ui_data.element_tree (dict): Simplified element tree
        """
        print('* Pre-process XML VH to clean-up as JSON and extract UI elements *')
        self.__ui_preprocessor.ui_vh_xml_cvt_to_json(ui_data=ui_data)
        self.__ui_preprocessor.ui_info_extraction(ui_data=ui_data)
        self.__ui_analyser.ui_build_element_tree(ui_data)
        return ui_data

    def analyze_ui(self, ui_data, ocr=True, cls=False):
        """
        Analyze ui to generate description for elements and hierarchical element tree
            1. Analyze UI element to attach description
            2. Build element tree based on the prev to represent the UI
        Args:
            ui_data (UIData): Target UI data for analysis
            ocr (bool): True to turn on ocr for the whole UI image
            cls (bool): True to turn on UI element classification
        Returns:
            ui_data.element['description']: 'description' attribute in element
            ui_data.element_tree (dict): structural element tree
        """
        print('* Analyze UI to generate an element tree with element descriptions *')
        self.__ui_analyser.ui_analysis_elements_description(ui_data=ui_data, ocr=ocr, cls=cls)
        self.__ui_analyser.ui_build_element_tree(ui_data)
        return ui_data

    '''
    ****************
    *** UI Check ***
    ****************
    '''
    def check_ui_decision_page(self, ui_data):
        """
        Check if the UI contain any following special components that require user intervention:
        1. UI Modal; 2. User Permission; 3. Login; 4. Form;
        Args:
            ui_data (UIData)
        Returns:
            response (dict): {"Component", "Explanation"}
        """
        print('* Check if UI requires user decision *')
        return self.__ui_checker.check_ui_decision_page(ui_data)

    '''
    ****************
    *** UI Utils ***
    ****************
    '''
    def annotate_elements_with_id(self, ui_data, only_leaves=True, show=False, draw_bound=False):
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
        print('* Annotate elements with their IDs on the screenshot image *')
        return self.__ui_util.annotate_elements_with_id(ui_data=ui_data, only_leaves=only_leaves, show=show, draw_bound=draw_bound)

