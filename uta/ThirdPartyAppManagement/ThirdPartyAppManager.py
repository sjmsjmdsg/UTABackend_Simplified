import time
import json
import re

from uta.config import *
from uta.ThirdPartyAppManagement._GooglePlay import _GooglePlay


class ThirdPartyAppManager:
    def __init__(self, model_manager):
        """
        Initialize ThirdPartyAppManager object.
        """
        self.__model_manager = model_manager
        self.__googleplay = _GooglePlay()

        self.__app_analyse_prompt = 'Summarize the main tasks that the app {title} can perform for senior users ' \
                                    'who are not familiar with it. ' \
                                    'Review the app description: "{description}". \n' \
                                    'Focus on specific functionality, presenting them as simple, user-friendly ' \
                                    'tasks. Each task should be distinct and cover only one aspect of the app. ' \
                                    'List the tasks in a format accessible to seniors, using clear examples where ' \
                                    'possible. End each task with a semicolon and start with a dash. \n' \
                                    'Example: \n' \
                                    '- Watch music videos and stay updated with trends; \n' \
                                    '- Subscribe to favorite channels for personalized content; \n' \
                                    '...and so on.'

        self.__apps_analysis_prompt = 'Analyze the list of apps and summarize the main tasks that each app can ' \
                                      'perform for senior users who are not familiar with them. Review each app\'s ' \
                                      'description and focus on specific functionality, presenting them as simple, ' \
                                      'user-friendly tasks. For each app, list its tasks in a format accessible to ' \
                                      'seniors, using clear examples where possible. Each task should be distinct ' \
                                      'and cover only one aspect of the app. List the tasks with a dash and end with ' \
                                      'a semicolon. Structure the output as a list of lists, where each inner list ' \
                                      'corresponds to the tasks of one app. \n' \
                                      'Example for a single app: \n' \
                                      '- Watch music videos and stay updated with trends; \n' \
                                      '- Subscribe to favorite channels for personalized content; \n' \
                                      '...and so on. \n\n' \
                                      'Apps to analyze: \n{app_details}'

        self.__availability_system_prompt = 'Identify the app related to the given task from the given app list. \n' \
                                           '!!!Note:\n ' \
                                           '1. ONLY use this JSON format to provide your answer: {{"App": "<app_package_or_None>", "Keywords": "<keywords or None>", "Reason": "<explanation>"}}.\n' \
                                           '2. If no related found, answer "None" for the "App" in the answer JSON.\n' \
                                           '3. If no related found, provide the keywords used to search relevant apps in the Google App store, otherwise "None". \n' \
                                           '!!!Examples\n:' \
                                           '1. {{"App": "com.whatsapp.com", "Keywords": "None", "Reason": "To send message in whatsapp, open the whatsapp app."}}.\n ' \
                                           '2. {{"App": "None", "Keywords": "Youtube", "Reason": "No app is related to the task \'watch a video\'."}}.\n'

        self.__availability_check_prompt = 'Given task: {task}\n' \
                                           'Given app list: {app_list}'

    @staticmethod
    def transfer_to_dict(resp):
        """
        Transfer string model returns to dict format
        Args:
            resp (dict): The model returns.
        Return:
            resp_dict (dict): The transferred dict.
        """
        try:
            return json.loads(resp['content'])
        except Exception as e:
            regex = r'"([A-Za-z ]+?)":\s*(".*?[^\\]"|\'.*?[^\\]\')|\'([A-Za-z ]+?)\':\s*(\'.*?[^\\]\'|".*?[^\\]")'
            attributes = re.findall(regex, resp['content'])
            resp_dict = {}
            for match in attributes:
                key = match[0] if match[0] else match[2]  # Select the correct group for the key
                value = match[1] if match[1] else match[3]  # Select the correct group for the value
                resp_dict[key] = value
            return resp_dict

    def conclude_app_functionality(self, tar_app, printlog=False):
        """
        Conclude the functionality of given app.
        Args:
            tar_app (dict): App including description, collected from google play
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Functionality of given app.
        """
        try:
            start = time.time()
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            new_conversation = self.__app_analyse_prompt.format(title=tar_app['title'],
                                                                description=tar_app['description'], printlog=printlog)
            conversations.append({'role': 'user', 'content': new_conversation})

            task_list = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            task_list = task_list.replace('\n', '').split(';')
            task_list = task_list[:-1] if len(task_list[-1]) == 0 else task_list
            task_list = [t.replace('\n', '').replace(' -', '-') for t in task_list]
            print('Running Time:%.3fs, ' % (time.time() - start))
            return task_list
        except Exception as e:
            raise e

    def conclude_multi_apps_functionalities(self, apps_list, printlog=False):
        """
        Conclude the functionality of a list of apps.
        Args:
            apps_list (list): List of apps, each including description, collected from Google Play.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            A list of lists, where each inner list contains the functionalities of a respective app.
        """
        try:
            start = time.time()
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            app_details = '\n'.join([f'- {app["title"]}: {app["description"]}' for app in apps_list])
            new_conversation = self.__apps_analysis_prompt.format(app_details=app_details, printlog=printlog)
            conversations.append({'role': 'user', 'content': new_conversation})

            response = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            app_sections = response.split('\n\n')
            task_list = []
            for section in app_sections:
                # Remove any leading or trailing whitespace and split the section into tasks
                tasks = section.replace('\n', '').strip().split(';')
                # Remove empty strings and extra spaces, and reformat tasks
                tasks = [task.strip().replace('\n', '').replace(' -', '-') for task in tasks if task.strip()]
                task_list.append(tasks)

            print('Running Time:%.3fs, ' % (time.time() - start))
            return task_list
        except Exception as e:
            raise e

    def check_related_apps(self, task, app_list, printlog=False):
        """
        Checks for apps related to a given task.
        Args:
            task (Task): The task for which related apps are to be found.
            app_list (list, optional): A list of apps to consider. If None, fetches from the device.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Related app (dict): {"App": "com.example.app", "Reason": "Directly performs the task"} or
                                {"App": "None", "Reason": "No app is related"}
        """
        try:
            print('* Check Related App *')
            # Format base prompt
            prompt = self.__availability_check_prompt.format(task=task.selected_task, app_list='; '.join(app_list))
            if len(task.user_clarify) > 0:
                prompt += '(Additional information and commands for the task:' + str(task.user_clarify) + '.)\n'
            if len(task.subtasks) > 0:
                prompt += '(Potential subtasks and steps to complete the task: ' + str(task.subtasks) + '.)\n'
            if len(task.except_apps) > 0:
                prompt += '(These apps cannot be launched or are proved to be unrelated to the task, ' \
                          'exclude them from your selection.\n' + str(task.except_apps) + '.)\n'
            # Ask FM
            conversations = [{'role': 'system', 'content': self.__availability_system_prompt},
                             {'role': 'user', 'content': prompt}]
            resp = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)
            task.res_related_app_check = self.transfer_to_dict(resp)
            print(task.res_related_app_check)
            return task.res_related_app_check
        except Exception as e:
            print(resp)
            raise e

    def recommend_apps(self, step, search_tar, fuzzy=False, max_return=5):
        """
        Recommends apps based on a search term and summarizes their functionalities.
        Args:
            step (AutoModeStep): AutoModeStep object containing current relation.
            search_tar (str): The search term or target app name.
            fuzzy (bool): If True, performs a fuzzy search, returning multiple related apps.
            max_return (int): The maximum number of apps to return in a fuzzy search.

        Returns:
            A list of dictionaries with app titles and their summarized functionalities.
        """
        try:
            if fuzzy:
                app_list = self.__googleplay.search_apps_fuzzy(search_tar)[:max_return]
                app_functions = self.conclude_multi_apps_functionalities(app_list)
                result = [{'title': app_list[idx]['title'], 'function': one_func} for idx, one_func in
                          enumerate(app_functions)]
            else:
                tar_app = self.__googleplay.search_app_by_name(search_tar)
                app_function = self.conclude_app_functionality(tar_app)
                result = [{'title': tar_app['title'], 'function': app_function}]
            step.app_recommendation_result = result
            return result
        except Exception as e:
            raise e

    def download_app(self, app_link):
        # need further discussion
        pass