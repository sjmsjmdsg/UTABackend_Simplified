import os
from os.path import join as pjoin

import cv2
from PIL import Image
import io

from uta.SystemConnection._Local import _Local
from uta.DataStructures import *
from uta.config import *


class SystemConnector:
    def __init__(self):
        """
        Initializes a SystemConnector instance.
        """
        self.__local = _Local()

        self.user_data_root = DATA_PATH

    '''
    ***************
    *** Data IO ***
    ***************
    '''
    def load_user(self, user_id):
        """
        Load user info from 'data/user_id/user.json'
        Args:
            user_id (str)
        Returns:
            user (User)
        """
        user_file = pjoin(self.user_data_root, user_id, 'user.json')
        if os.path.exists(user_file):
            user = User(user_id=user_id)
            user.load_from_dict(self.load_json(user_file))
            print('- Import user info from file', user_file, '-')
            return user
        else:
            # raise FileNotFoundError(f"The user file {user_file} does not exist.")
            return None

    def save_user(self, user):
        """
        Save user info under the user folder
        'data/user_id/user.json'
        Args:
            user (User)
        """
        user_folder = pjoin(self.user_data_root, user.user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            print('- Create user folder', user_folder, '-')
        user_file = pjoin(user_folder, 'user.json')
        self.save_json(user.to_dict(), user_file)
        print('- Export user info to', user_file, '-')

    def load_task(self, user_id, task_id):
        """
        Retrieve task if exists or create a new task if not
        'data/user_id/task_id/task.json'
        Args:
            user_id (str): User id, associated to the folder named with the user_id
            task_id (str): Task id, associated to the json file named with task in the user folder
        Return:
            Task (Task) if exists: Retrieved or created Task object
            None if not exists
        """
        user_folder = pjoin(self.user_data_root, user_id)       # 'data/user_id'
        task_file = pjoin(user_folder, task_id, 'task.json')    # 'data/user_id/task_id/task.json'
        if os.path.exists(task_file):
            task = Task(task_id=task_id, user_id=user_id)
            task.load_from_dict(self.load_json(task_file))
            print('- Import task from file', task_file, '-')
            return task
        else:
            return None

    def save_task(self, task):
        """
        Save Task object to json file under the associated user folder, and with the file name of task id
        'data/user_id/task_id/task.json'
        Args:
            task (Task): Task object
        """
        task_folder = pjoin(self.user_data_root, task.user_id, task.task_id)
        if not os.path.exists(task_folder):
            os.makedirs(task_folder)
            # print('- Create task folder', task_folder, '-')
        task_file = pjoin(task_folder, 'task.json')
        self.save_json(task.to_dict(), task_file)
        # print('- Export task to file', task_file, '-')

    @staticmethod
    def load_ui_data(screenshot_file, xml_file=None, ui_resize=(1080, 2280)):
        """
        Load UI to UIData
        Args:
            screenshot_file (path): Path to screenshot image
            xml_file (path): Path to xml file if any
            ui_resize (tuple): Specify the size/resolution of the UI
        Returns:
            self.ui_data (UIData)
        """
        return UIData(screenshot_file, xml_file, ui_resize)

    def save_ui_data(self, ui_data, output_dir):
        """
        Save UIData to files, including elements and tree
        Save to 'data/user_id/task_id/ui_id_element.json', 'data/user_id/task_id/ui_id_uitree.json'
        Args:
            ui_data (UIData): UIData object to save
            output_dir (str): The output directory, usually under 'data/user_id/task_id/'
        """
        # output_file_path_elements = pjoin(output_dir, ui_data.ui_id + '_elements.json')
        # self.save_json(ui_data.elements, output_file_path_elements)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            # print('- Create ui folder', output_dir, '-')
        output_file_path_element_tree = pjoin(output_dir, ui_data.ui_id + '_uitree.json')
        self.save_json(ui_data.elements, output_file_path_element_tree)
        # print('- Export ui elements to file', output_file_path_element_tree, '-')

        # save annotated screenshot
        if ui_data.annotated_elements_screenshot is not None:
            ui_data.annotated_elements_screenshot_path = pjoin(output_dir, ui_data.ui_id + '_annotated_elements.png')
            cv2.imwrite(ui_data.annotated_elements_screenshot_path, ui_data.annotated_elements_screenshot)
            # print('- Export annotated elements screenshot to file', ui_data.annotated_elements_screenshot_path, '-')

    '''
    ****************
    *** Local IO ***
    ****************
    '''
    def load_xml(self, file_path, encoding='utf-8'):
        """
        Loads and parses an XML file.
        Args:
            file_path (str): Path to the XML file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed XML content.
        """
        return self.__local.load_xml(file_path, encoding)

    def load_img(self, file_path):
        """
        Loads an image file as a binary stream.
        Args:
            file_path (str): Path to the image file.
        Returns:
            Binary content of the image file.
        """
        return self.__local.load_img(file_path)

    def load_json(self, file_path, encoding='utf-8'):
        """
        Loads a JSON file.
        Args:
            file_path (str): Path to the JSON file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed JSON data.
        """
        return self.__local.load_json(file_path, encoding)

    def save_xml(self, file, file_path, encoding='utf-8'):
        """
        Saves a dictionary as an XML file.
        Args:
            file (dict): Dictionary to save as XML.
            file_path (str): Path where the XML file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_xml(file, file_path, encoding)

    def save_img(self, img, file_path):
        """
        Saves binary image data to a file.
        Args:
            img (bytes): Binary image data to save.
            file_path (str): Path where the image file will be saved.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_img(img, file_path)

    def save_json(self, json_obj, file_path, encoding='utf-8'):
        """
        Saves a dictionary as a JSON file.
        Args:
            json_obj (dict): Dictionary to save as JSON.
            file_path (str): Path where the JSON file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.__local.save_json(json_obj, file_path, encoding)


if __name__ == '__main__':
    sys_connector = SystemConnector()
