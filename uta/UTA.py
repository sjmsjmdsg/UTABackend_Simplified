import time
from os.path import join as pjoin
import traceback
import cv2

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.SystemConnection import SystemConnector
from uta.AvailableTaskList import TaskList
from uta.TaskAction import TaskActionChecker
from uta.ThirdPartyAppManagement import ThirdPartyAppManager
from uta.UIProcessing import UIProcessor


class UTA:
    def __init__(self):
        """
        Initialize the UTA class with necessary modules and user data paths.
        """
        # basics
        self.model_manager = ModelManager()
        self.system_connector = SystemConnector()
        # workers
        self.ui_processor = UIProcessor(self.model_manager)
        self.task_list = TaskList(self.model_manager)
        self.task_action_checker = TaskActionChecker(self.model_manager)
        self.app_recommender = ThirdPartyAppManager(self.model_manager)
        # current data
        self.cur_user = None  # User object, current user
        self.cur_task = None  # Task object, current task

    '''
    *************
    *** Setup ***
    *************
    '''
    def setup_user(self, user_id, device_resolution, app_list):
        """
        Set up folders for user, and store user info into the user.json
        'data/user_id/user.json
        Args:
            user_id (str): Identifier for the user.
            device_resolution (tuple): Specify the size/resolution of the UI
            app_list (list): List of the names of installed apps
        """
        user = User(user_id=user_id, device_resolution=device_resolution, app_list=app_list)
        self.system_connector.save_user(user)
        self.cur_user = user
        return user

    def instantiate_user_task(self, user_id, task_id, user_msg=None):
        """
        Instantiate a User object to get the user info
        Instantiate a Task object by loading an existing one or creating a new one according to the given info
        Args:
            user_id (str): User id to identify the folder
            task_id (str): Task id to identify the file
            user_msg (str): User's input message. For new task, it is the task description. For existing task, append it to conversation.
        Returns:
            user (User): User object to store user info
            task (Task): Task object
        """
        user = self.system_connector.load_user(user_id=user_id)
        task = self.system_connector.load_task(user_id=user_id, task_id=task_id)
        # if the task does not exist, creat a new one within the user's folder
        if not task:
            task = Task(task_id=task_id, user_id=user_id, task_description=user_msg)
        else:
            if user_msg:
                if task.res_task_match.get('State') and 'related' in task.res_task_match['State'].lower() or \
                        task.res_task_match.get('State') is None and 'related' in str(task.res_task_match).lower():
                    task.clarification_user_msg = user_msg
                else:
                    task.selected_task = user_msg
                    task.involved_app = self.task_list.app_list[self.task_list.available_task_list.index(user_msg)]
                    # task.step_hint = self.task_list.step_list[self.task_list.available_task_list.index(user_msg)]
        self.cur_user = user
        self.cur_task = task
        return user, task

    '''
    ************************
    *** Task Declaration ***
    ************************
    '''
    def fetch_available_task_list(self):
        """
        Fetch the current available task list
        Return:
            available_task_list (list): list of task descriptions (string)
        """
        return self.task_list.available_task_list, self.task_list.task_info_list

    def fetch_hardcode_task_list(self):
        """
        Fetch the hard code task list
        Return:
            hard_code_task_list (list): list of task descriptions (string)
        """
        return self.task_list.available_task_list, self.task_list.task_info_list

    def declare_task(self, user_id, task_id, user_msg):
        """
        Declare the task.
        First, clarify it, if unclear, return response to the frontend for user feedback.
        Second, if already clear, decompose the task to atomic tasks if necessary
        Args:
            user_id (str): User id, associated to the folder named with the user_id
            task_id (str): Task id, associated to the json file named with task in the user folder
            user_msg (str): User's input message.
        """
        try:
            print('\n*** Declare task ***')
            user, task = self.instantiate_user_task(user_id, task_id, user_msg)

            if task.involved_app is not None:
                match_app = self.task_list.match_app_to_applist(task, user.app_list)
                self.system_connector.save_task(task)
                return match_app

            declare_resp = self.task_list.match_task_to_list(task)
            self.system_connector.save_task(task)
            return declare_resp
        except Exception as e:
            error_trace = traceback.format_exc()
            action = {"Action": "Error at the backend.", "Exception": e, "Traceback": error_trace}
            print(action)
            return action

    '''
    ***********************
    *** Task Automation ***
    ***********************
    '''
    def auto_task(self, task_desc, task_id, device,
                  max_try=10, show_ui=False, printlog=False, wait_time=3):
        """
        Automate the task on the device directly
        Args:
            task_desc (str): The description of the task
            task_id (str): Used to store the processing results under the folder "data/test/task_id"
            device (Device): Device to operate
            max_try (int): The maximum number of attempts
            show_ui (bool): True to show the annotated UI and the actions to be performed
            printlog (bool): True to print the log of large model
            wait_time (int): Seconds to wait for the loading of new page before
        Returns:
            Output and perform the action on the device
        """
        # 0. retrieve task info
        task = Task(task_id=task_id, user_id='test', task_description=task_desc)
        self.cur_task = task
        task.selected_task = task_desc
        task.keyboard_active = device.check_keyboard_active()
        output_dir = pjoin(self.system_connector.user_data_root, 'test', task_id)

        for i in range(max_try):
            print('\n*** UI ', i, '***')
            # 1. process ui
            ui_img_file, ui_xml_file = device.cap_and_save_ui_screenshot_and_xml(ui_id=len(task.relations), output_dir=output_dir)
            ui = self.process_ui_data(ui_img_file, ui_xml_file, device.get_device_resolution(), show=show_ui)
            self.system_connector.save_ui_data(ui, output_dir=output_dir)

            # 2. check action
            task.conversation_automation = []  # clear up the conversation of previous ui
            # check action on the UI by checking the relation and target elements
            action = self.task_action_checker.action_on_ui_vision(ui, task, printlog)
            action = self.set_action(action)
            self.system_connector.save_task(task)
            print(action)

            # 3. perform action
            if action['Action'] == 'Complete':
                if show_ui and action.get('ElementBounds'):
                    bounds = action['ElementBounds']
                    device.mark_circle_on_element_centroid(((int(bounds[2]) + int(bounds[0])) // 2, (int(bounds[3]) + int(bounds[1])) // 2), ui.ui_screenshot.copy())
                print('*** Task Complete ***')
                break
            else:
                device.take_action(action=action, ui_data=ui, show=show_ui)
            print('* Waiting for loading page *')
            time.sleep(wait_time)

    def check_action_on_ui(self, user_id, task_id, ui_img_file, ui_xml_file, task_desc, resolution, keyboard_active, show=False):
        """
        Process UI (Annotate the UI element IDs) and check the relation and action on this UI for the task
        Args:
            user_id (str): ui id
            task_id (str): task id
            ui_img_file (path): The path of the UI screenshot image
            ui_xml_file (path): The path of the UI XML file
            task_desc (str): The description of the task
            resolution (tuple): Resolution of the screen
            keyboard_active (bool): True to indicate the keyboard is active in this UI
            show (bool): Whether show UI and printlog
        """
        # 0. initial task
        task = Task(task_id=task_id, user_id=user_id, task_description=task_desc)
        task.selected_task = task_desc
        task.keyboard_active = keyboard_active
        # 1. process ui
        ui = self.process_ui_data(ui_img_file, ui_xml_file, resolution, show=show)
        self.system_connector.save_ui_data(ui, output_dir=pjoin(self.system_connector.user_data_root, 'test/100'))
        # 2. check action
        action = self.task_action_checker.action_on_ui_vision(ui, task, printlog=show)
        action = self.set_action(action)
        print(action)
        return ui, action

    def automate_task_vision(self, user_id, task_id, ui_img_file, ui_xml_file, printlog=False):
        """
        Identify the action on the current ui to automate the task based on GPT-4V
        Args:
            user_id (str): ui id
            task_id (str): task id
            ui_img_file (path): screenshot image path
            ui_xml_file (path): VH xml file path
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action": }
        """
        try:
            # 0. retrieve task info
            user, task = self.instantiate_user_task(user_id, task_id)

            # 1. process ui
            ui = self.process_ui_data(ui_img_file, ui_xml_file, user.device_resolution, show=printlog)
            self.system_connector.save_ui_data(ui, output_dir=pjoin(self.system_connector.user_data_root, user_id, task_id))

            # 2. act step
            task.conversation_automation = []  # clear up the conversation of previous ui
            # check action on the UI by checking the relation and target elements
            action = self.task_action_checker.action_on_ui_vision(ui, task, printlog)
            action = self.set_action(action)
            self.system_connector.save_task(task)
            return ui, action

        except Exception as e:
            error_trace = traceback.format_exc()
            action = {"Action": "Error at the backend.", "Exception": e, "Traceback": error_trace}
            print(action)
            return None, action

    def automate_task(self, user_id, task_id, ui_img_file, ui_xml_file,
                      package_name=None, activity_name=None, keyboard_active=False, printlog=False):
        """
        Identify the action on the current ui to automate the task
        Args:
            user_id (str): ui id
            task_id (str): task id
            ui_img_file (path): Screenshot image path
            ui_xml_file (path): VH xml file path
            package_name (str): Current app name
            activity_name (str): Current page name
            keyboard_active (bool): If the keyboard is active, can only input text when the keyboard is active
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action": }
        """
        try:
            # 0. retrieve task info
            user, task = self.instantiate_user_task(user_id, task_id)
            task.cur_package = package_name
            task.cur_activity = activity_name
            task.keyboard_active = keyboard_active

            # 1. process ui
            ui = self.process_ui_data(ui_img_file, ui_xml_file, user.device_resolution)
            self.system_connector.save_ui_data(ui, output_dir=pjoin(self.system_connector.user_data_root, user_id, task_id))

            # 2. act step
            task.conversation_automation = []  # clear up the conversation of previous ui
            # check action on the UI by checking the relation and target elements
            action = self.task_action_checker.action_on_ui(ui, task, printlog)
            action = self.set_action(action)
            self.system_connector.save_task(task)
            return ui, action
        except Exception as e:
            error_trace = traceback.format_exc()
            action = {"Action": "Error at the backend.", "Exception": e, "Traceback": error_trace}
            print(action)
            return None, action

    @staticmethod
    def set_action(action):
        # if not complete, check if the UI is user decision page
        if (action.get('Relation') and 'user action' in action['Relation'].lower() or
                action.get('Relation') is None and 'user action' in str(action).lower()) or \
            (action.get('Relation') and 'sensitive action' in action['Relation'].lower() or
                action.get('Relation') is None and 'sensitive action' in str(action).lower()):
            action = {"Action": "User Decision", **action}
            return action

        # if go back and element id, click element
        if action.get('Action') and 'back' in action['Action'].lower():
            if action.get('Element Id') and 'none' not in str(action['Element Id']).lower() or \
                    action.get('Element Id') is None and 'none' not in str(action).lower():
                action["Action"] = "Click"
                return action

        # if complete
        if action.get('Relation') and 'complete' in action['Relation'].lower() or \
                action.get('Relation') is None and 'complete' in str(action).lower():
            action["Action"] = "Complete"
            return action
        return action

    def process_ui_data(self, ui_img_file, ui_xml_file, device_resolution, show=False, annotate_bound=True):
        """
        Process ui dato
        Args:
            ui_img_file (path): Screenshot image path
            ui_xml_file (path): VH xml file path
            device_resolution (tuple): Device resolution
            show (bool): True to show the detection result
            annotate_bound (bool): True to draw bounding boxes for elements in annotation
        Return:
            annotated_ui (image): ui with processing results
        """
        ui = self.system_connector.load_ui_data(screenshot_file=ui_img_file, xml_file=ui_xml_file, ui_resize=device_resolution)
        self.ui_processor.preprocess_ui(ui)
        ui.annotated_elements_screenshot = self.ui_processor.annotate_elements_with_id(ui, show=show, draw_bound=annotate_bound)
        # resize image
        # annotated_elements_screenshot = cv2.resize(annotated_elements_screenshot, (device_resolution[0]//4, device_resolution[1]//4))
        return ui


if __name__ == '__main__':
    uta = UTA()
    uta.automate_task('user1', 'task3', ui_img_file='../data/user1/task3/0.png',
                      ui_xml_file='../data/user1/task3/0.xml')
