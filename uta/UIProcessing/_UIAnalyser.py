import time
import copy


class _UIAnalyser:
    """
    Analyze UI raw data for element description and element tree
    """
    def __init__(self, model_manager=None):
        self.__model_manager = model_manager

    '''
    *******************
    *** UI Analysis ***
    *******************
    '''
    def ui_analysis_elements_description(self, ui_data, ocr=True, cls=False):
        """
        Extract description for UI elements through 'text', 'content-desc', 'classification' and 'caption'
        Args:
            ui_data (UIData): Target UI data for analysis
            ocr (bool): True to turn on ocr for the whole UI image
            cls (bool): True to turn on UI element classification
        Returns:
            ui_data.element['description']: 'description' attribute in element
        """
        def extract_element_description(ele):
            """
            Extract element description from 'text', 'content-desc', 'icon-cls' and 'caption'
            Args:
                ele (dict): UI element
            Returns:
                element.description (str): the description of this element
            """
            description = ''
            # check text
            if 'text' in ele and len(ele['text']) > 0:
                description += ele['text']
            # check content description
            if 'content-desc' in ele and len(ele['content-desc']) > 0 and ele['content-desc'] != ele['text']:
                description = ele['content-desc'] if len(description) == 0 else description + ' / ' + ele['content-desc']
            # if no text and content description, check caption
            if len(description) == 0:
                if 'icon-cls' in ele and ele['icon-cls']:
                    description = ele['icon-cls']
                elif 'caption' in ele and '<unk>' not in ele['caption']:
                    description = ele['caption']
                else:
                    description = None
            ele['description'] = description

        # print('* Analyse descriptions for elements *')
        # use ocr to detect text
        if ocr:
            s1 = time.time()
            self.ocr_detect_ui_text(ui_data)
            print('OCR Time: %.3fs' % (time.time() - s1))
        # classify non-text elements
        if cls:
            s2 = time.time()
            self.classify_elements(ui_data)
            print('CLs Time: %.3fs' % (time.time() - s2))
        # extract element description from 'text', 'content-desc', 'icon-cls' and 'caption'
        for element in ui_data.elements_leaves:
            extract_element_description(element)

    def ocr_detect_ui_text(self, ui_data):
        """
        Detect text on UI through OCR
        Args:
            ui_data (UIData): Target UI data for analysis
        Returns:
            ui_data.ocr_text: UI ocr detection result, list of __texts {}
            ui_data.elements_leaves['text']: store text content for each element
        """
        def match_text_and_element(ele):
            """
            Match ocr text and element through iou
            """
            for text in ui_data.ocr_text:
                t_b, e_b = text['bounds'], ele['bounds']
                # calculate intersected area between text and element
                intersected = max(0, min(t_b[2], e_b[2]) - max(t_b[0], e_b[0])) \
                              * max(0, min(t_b[3], e_b[3]) - max(t_b[1], e_b[1]))
                if intersected > 0:
                    ele['ocr'] += text['content']
                    ele['text'] += text['content']

        # google ocr detection for the GUI image
        ui_data.ocr_text = self.__model_manager.detect_text_ocr(img_path=ui_data.screenshot_file)
        # merge text to elements according to position
        for element in ui_data.elements_leaves:
            if element['text'] == '':
                element['ocr'] = ''
                match_text_and_element(element)

    def classify_elements(self, ui_data):
        """
        Classify element using the icon classification model
        Args:
            ui_data (UIData): Target UI data for analysis
        Returns:
            ui_data.elements_leaves['icon-cls']: class of icon if any, otherwise None
        """
        elements = ui_data.elements_leaves
        clips = []
        for ele in elements:
            bound = ele['bounds']
            clips.append(ui_data.ui_screenshot[bound[1]: bound[3], bound[0]:bound[2]])
        classes = self.__model_manager.classify_icons(clips)
        for i, ele in enumerate(elements):
            if classes[i][1] > 0.95:
                ele['icon-cls'] = classes[i][0]
            else:
                ele['icon-cls'] = None

    '''
    ***********************
    *** Structural Tree ***
    ***********************
    '''
    def ui_build_element_tree(self, ui_data):
        """
        Build a hierarchical element tree with a few key attributes to represent the vh
        Args:
            ui_data (UIData): Target UI data for analysis
        Returns:
            ui_data.element_tree (dict): structural element tree
        """
        # print('* Organize simplified element tree *')
        ui_data.element_tree = self.__combine_children_to_tree(ui_data=ui_data, start_element=ui_data.elements[0])
        # json.dump(ui_data.element_tree, open(ui_data.output_file_path_element_tree, 'w'), indent=4)
        # print('Save element tree to', self.output_file_path_element_tree)

    def __combine_children_to_tree(self, ui_data, start_element):
        """
        Combine the element's children to a tree recursively
        Args:
            ui_data (UIData): The whole UIData for finding elements by ids
            start_element (UIData.elements[n], dict): The start element to merge children
        Returns:
            element (dict): Element with children combined and attributes simplified
        """
        element_cp = copy.deepcopy(start_element)
        if 'children-id' in element_cp:
            element_cp['children'] = []
            for c_id in element_cp['children-id']:
                element_cp['children'].append(self.__combine_children_to_tree(ui_data=ui_data,
                                                                              start_element=ui_data.elements[c_id]))
            self.__select_ele_attr(element_cp, ['scrollable', 'id', 'resource-id', 'class', 'clickable',
                                                'children', 'description'])
        else:
            self.__select_ele_attr(element_cp, ['id', 'resource-id', 'class', 'clickable', 'children', 'description'])
        self.__simplify_ele_attr(element_cp)
        return element_cp

    @staticmethod
    def __select_ele_attr(element, selected_attrs):
        """
        Select certain attributes in a dict
        Args:
            element (dict): Element with attributes
            selected_attrs (list): List of selected attributes
        Returns:
            element (dict): Elements with selected attributes
        """
        element_cp = copy.deepcopy(element)
        for key in element_cp.keys():
            if key == 'selected' and element[key]:
                continue
            if key not in selected_attrs or element[key] is None or element[key] == '':
                del(element[key])

    @staticmethod
    def __simplify_ele_attr(element):
        """
        Rename and simplify attributes
        Args:
            element (dict): Element with attributes
        Returns:
            element (dict): Elements with simplified attributes
        """
        if 'resource-id' in element:
            element['resource-id'] = element['resource-id'].replace('com', '')
            element['resource-id'] = element['resource-id'].replace('android', '')
            element['resource-id'] = element['resource-id'].replace('..', '.')
            element['resource-id'] = element['resource-id'].replace('.:', ':')
        if 'class' in element:
            element['class'] = element['class'].replace('android', '')
            element['class'] = element['class'].replace('..', '.')
            element['class'] = element['class'].replace('.:', ':')
