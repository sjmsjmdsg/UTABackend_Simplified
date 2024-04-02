import copy
import xmltodict


class _UIPreProcessor:
    """
    Preprocess UI xml raw data by cleaning up vh and convert to json
    """
    def __init__(self):
        pass

    '''
    ******************************************
    *** Convert the VH to Rico format JSON ***
    ******************************************
    '''
    def ui_vh_xml_cvt_to_json(self, ui_data):
        """
        Convert xml vh to json format for easier processing
        Args:
            ui_data (UIData): ui data for processing
        Returns:
             ui_data.ui_vh_json (dict): VH in a tidy json format
        """
        # print('* Reformat xml vh *')
        ui_data.ui_vh_json = xmltodict.parse(open(ui_data.xml_file, 'r', encoding='utf-8').read())
        # Tidy up and reformat the json vh into Rico format
        ui_data.ui_vh_json = {'activity': {'root': self.__cvt_node_to_rico_format(ui_data.ui_vh_json['hierarchy']['node'])}}

    def __cvt_node_to_rico_format(self, node):
        """
        Recursively reformat ui element node to rico format
        Args:
            node: ui element node in the dict
        Return:
            Reformatted node
        """
        node = self.__reformat_node(node)
        if 'children' in node:
            if type(node['children']) == list:
                new_children = []
                for child in node['children']:
                    new_children.append(self.__cvt_node_to_rico_format(child))
                node['children'] = new_children
            else:
                node['children'] = [self.__cvt_node_to_rico_format(node['children'])]
        return node

    @staticmethod
    def __reformat_node(node):
        """
        Tidy up node attributes
        """
        node_new = {}
        for key in node.keys():
            if node[key] == 'true':
                node[key] = True
            elif node[key] == 'false':
                node[key] = False

            if key == 'node':
                node_new['children'] = node['node']
            elif key == '@bounds':
                node_new['bounds'] = eval(node['@bounds'].replace('][', ','))
            # elif key == '@index':
            #     continue
            else:
                node_new[key.replace('@', '')] = node[key]
        return node_new

    '''
    **************************
    *** UI Info Extraction ***
    **************************
    '''
    def ui_info_extraction(self, ui_data):
        """
        Extract elements from raw view hierarchy Json file and store them as dictionaries
        Args:
            ui_data (UIData): ui data for processing
        Returns:
            ui_data.elements; ui_data.elements_leaves (list of dicts)
        """
        # print('* Extract ui elements from vh *')
        json_vh = ui_data.ui_vh_json
        json_cp = copy.deepcopy(json_vh)
        element_root = json_cp['activity']['root']
        element_root['class'] = 'root'
        # clean up the json tree to remove redundant layout node
        self.__prone_invalid_children(element_root)
        self.__remove_redundant_nesting(element_root)
        self.__merge_element_with_single_leaf_child(element_root)
        # build hierarchy
        self.__extract_children_elements(ui_data, element_root, 0)
        self.__gather_leaf_elements(ui_data)
        # json.dump(self.elements, open(self.output_file_path_elements, 'w', encoding='utf-8'), indent=4)
        # print('Save elements to', self.output_file_path_elements)

    def __prone_invalid_children(self, element):
        """
        Prone invalid children elements
        Leave valid children and prone their children recursively
        Take invalid children's children as its own directly
        """
        def check_if_element_valid(ele, min_length=5):
            """
            Check if the element is valid and should be kept
            """
            if (ele['bounds'][0] >= ele['bounds'][2] - min_length
                or ele['bounds'][1] >= ele['bounds'][3] - min_length) \
                    or ('layout' in ele['class'].lower() and not ele['clickable']):
                return False
            return True

        valid_children = []
        if 'children' in element:
            for child in element['children']:
                if check_if_element_valid(child):
                    valid_children.append(child)
                    self.__prone_invalid_children(child)
                else:
                    valid_children += self.__prone_invalid_children(child)
            element['children'] = valid_children
        return valid_children

    def __remove_redundant_nesting(self, element):
        """
        Remove redundant parent node whose bounds are same
        """
        if 'children' in element and len(element['children']) > 0:
            redundant = False
            new_children = []
            for child in element['children']:
                # inherit clickability
                if element['clickable']:
                    child['clickable'] = True
                # recursively inspect child node
                new_children += self.__remove_redundant_nesting(child)
                if child['bounds'] == element['bounds']:
                    redundant = True
            # only return the children if the node is redundany
            if redundant:
                return new_children
            else:
                element['children'] = new_children
        return [element]

    def __merge_element_with_single_leaf_child(self, element):
        """
        Keep the resource-id and class and clickable of the child element
        """
        if 'children' in element:
            if len(element['children']) == 1 and 'children' not in element['children'][0]:
                child = element['children'][0]
                element['resource-id'] = child['resource-id'] if 'resource-id' in child else None
                element['class'] = child['class']
                element['clickable'] = child['clickable']
                del element['children']
            else:
                new_children = []
                for child in element['children']:
                    new_children.append(self.__merge_element_with_single_leaf_child(child))
                element['children'] = new_children
        return element

    def __extract_children_elements(self, ui_data, element, layer):
        """
        Recursively extract children from an element
        Args:
            ui_data (UIData)
            element (dict): dict node with attributes and hierarchical elements
            layer (int): number of layer for the current element
        Returns:
             children_depth (int): maximum depth of children nodes
        """
        element['id'] = ui_data.elements_ids
        element['layer'] = layer
        ui_data.elements.append(element)
        children_depth = layer  # record the depth of the children
        if 'children' in element and len(element['children']) > 0:
            element['children-id'] = []
            for child in element['children']:
                ui_data.elements_ids += 1
                element['children-id'].append(ui_data.elements_ids)
                children_depth = max(children_depth, self.__extract_children_elements(ui_data, child, layer + 1))
            element['children-depth'] = children_depth
            # replace wordy 'children' with 'children-id'
            del element['children']
        if 'ancestors' in element:
            del element['ancestors']
        return children_depth

    @staticmethod
    def __gather_leaf_elements(ui_data):
        """
        Gather all leaf elements that have no children together
        """
        i = 0
        for ele in ui_data.elements:
            if 'children-id' not in ele:
                ele['leaf-id'] = i
                ui_data.elements_leaves.append(ele)
                i += 1
            else:
                ele['class'] += '(container)'