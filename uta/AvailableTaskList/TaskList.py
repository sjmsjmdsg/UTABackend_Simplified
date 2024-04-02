import json
import re


class TaskList:
    def __init__(self, model_manager):
        self.available_task_list = ['Manage the pin for the device', 'Connect to Wi-Fi', 'Open Bluetooth',
                                    'Change the font size of the phone', 'Adjust screen brightness', 'Change wallpapers for my device',
                                    'Send text messages to friend with Whatsapp', 'Make video calls to friend with Whatsapp', 'Add a new contact in Whatsapp',
                                    'Change privacy settings of Whatsapp', 'Change ringtone of Whatsapp', 'Block unwanted contacts in Whatsapp',
                                    'Host a meeting with Zoom', 'Join a meeting with Zoom', 'Schedule a meeting with Zoom',
                                    'Share the screen of the Android device with Zoom', 'View reminders in Zoom', 'Scan QR code via Zoom',
                                    'Watch news with YouTube', 'Subscribe to Telstra channel in Youtube', 'Like/dislike video in YouTube',
                                    'Comment on videos in YouTube', 'Adjust video quality in YouTube', 'Add video to watch later in YouTube',
                                    'Find products with Temu', 'Check product’s customer reviews with Temu', 'Check carts in Temu',
                                    'Save favourite items for future view in Temu', 'Enter the check out page in Temu', 'help me to look for contact ways of customer service',

                                    'Ask Chatgpt to translate "How are you" into French', 'Explore GPTs and ask Planty GPTs in Chatgpt about "How to take care citrus"', "View my account information in Chatgpt",
                                    'Change main language of Chatgpt', 'Archive current dialogs in Chatgpt', 'Find archived dialogs in Chatgpt',
                                    'Open pdf file in PDF Reader', 'Sort pdf files by size in PDF Reader', 'Open word file in PDF Reader',
                                    'Mark pdf file favourite in PDF Reader', 'Convert word into pdf in PDF Reader', 'Change language to English in PDF Reader',
                                    'Search hotel in Melbourne in Booking.com', 'Search One-way flight to Melbourne in Booking.com', 'Search car rental pick up in Melbourne CBD with driver\'s age around 65 in Booking.com',
                                    'Search hotel in Melbourne and sorted by price in Booking.com', 'Search hotel in Melbourne with free parking features in Booking.com', 'Search hotel in Melbourne and view the comments in Booking.com',
                                    'View the available car types to airport in Uber', 'View the possible fast food that can be delivered in Uber', 'View my account info in Uber',
                                    'View the possible fast food that can be delivered under $1 delivery fee in Uber', 'Find Guzman y Gomez in food deliver in Uber', 'Look at details of battered Fish in Guzman y Gomez in food deliver in Uber',
                                    'Find nearby restaurant by Google map', 'Find nearby restaurant by Google map and sorted by price', 'Find nearby Asian restaurant by Google map and sorted by price',
                                    'Find nearby restaurant by Google map and show the directions by bus', 'Find nearby restaurant by Google map and show the directions by walk and start guiding', 'Set home address in Google map']

        self.task_info_list = [('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Settings', 'Feasible'), ('Settings', 'Feasible'), ('Settings', 'Feasible'),
                               ('Communications', 'Feasible'), ('Communications', 'Feasible'), ('Communications', 'Feasible'),
                               ('Communications', 'Feasible'), ('Communications', 'Feasible'), ('Communications', 'Feasible'),
                               ('Business', 'Feasible'), ('Business', 'Feasible'), ('Business', 'Feasible'),
                               ('Business', 'Feasible'), ('Business', 'Feasible'), ('Business', 'Feasible'),
                               ('Media & Video', 'Feasible'), ('Media & Video', 'Feasible'), ('Media & Video', 'Feasible'),
                               ('Media & Video', 'Feasible'), ('Media & Video', 'Feasible'), ('Media & Video', 'Feasible'),
                               ('Shopping', 'Feasible'), ('Shopping', 'Feasible'), ('Shopping', 'Infeasible'),
                               ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible'), ('Shopping', 'Infeasible'),
                               ('Productivity', 'Feasible'), ('Productivity', 'Feasible'), ('Productivity', 'Feasible'),
                               ('Productivity', 'Feasible'), ('Productivity', 'Feasible'), ('Productivity', 'Feasible'),
                               ('Productivity', 'Feasible'), ('Productivity', 'Feasible'), ('Productivity', 'Feasible'),
                               ('Productivity', 'Feasible'), ('Productivity', 'Feasible'), ('Productivity', 'Feasible'),
                               ('Travel & Local', 'Infeasible'), ('Travel & Local', 'Infeasible'), ('Travel & Local', 'Infeasible'),
                               ('Travel & Local', 'Infeasible'), ('Travel & Local', 'Infeasible'), ('Travel & Local', 'Infeasible'),
                               ('Maps & Navigation', 'Infeasible'), ('Maps & Navigation', 'Infeasible'), ('Maps & Navigation', 'Infeasible'),
                               ('Maps & Navigation', 'Infeasible'), ('Maps & Navigation', 'Infeasible'), ('Maps & Navigation', 'Infeasible'),
                               ('Maps & Navigation', 'Feasible'), ('Maps & Navigation', 'Feasible'), ('Maps & Navigation', 'Feasible'),
                               ('Maps & Navigation', 'Feasible'), ('Maps & Navigation', 'Feasible'), ('Maps & Navigation', 'Feasible'),
                               ]

        self.app_list = ['Android Settings'] * 6 + ['Whatsapp'] * 6 + ['Zoom'] * 6 + ['Youtube'] * 6 + ['Temu'] * 6 + \
                        ['Chatgpt'] * 6 + ['PDF Reader'] * 6 + ['Booking.com'] * 6 + ['Uber'] * 6 + ['Google Map'] * 6

        self.step_list = ["Tap search bar TextView > search Lock > Tap Lock screen password Textview with \"Password & security\" > Tap Lock screen password Textview > when you see Numeric TextView, the task is Almost Completed and STOP THE TASK.",
                          "Tap Wi-Fi TextView > when you see Wi-Fi Switch, the task is Almost Completed and STOP THE TASK, and you should mention user to open the Wi-Fi switch to enable and select Wi-Fi user wants.",
                          "Tap Bluetooth TextView > when you see Bluetooth Switch, the task is Almost Completed and STOP THE TASK, and you should mention user to open the Bluetooth switch to enable Bluetooth.",
                          "Tap search bar TextView > search Font > After search, tap Font Textview with Display breadcrumb, DO NOT repeat the search op > when you see a seekbar for adjusting the font size, you should mention user to slide the Font size slide bar to adjust font size, and the task is Almost Completed and STOP THE TASK.",
                          "Tap search bar TextView > search brightness > After search, tap Brightness Textview with Display breadcrumb, DO NOT repeat the seach op > when you see Light mode with a Radio button, you should mention user to slide the Brightness slide bar to adjust brightness, and the task is Almost Completed and STOP THE TASK.",
                          "Tap Wallpapers & style TextView > Tap Wallpapers > Tap wallpaper thumbnail1 > when you see Apply Button, you should mention user to choose wanted wallpaper and apply, and the task is Almost Completed and STOP THE TASK.",

                          "Tap Send message Button > Tap Mulong TextView > Tap message EditText > Input greeting info > The task is Almost Completed and STOP THE TASK.",
                          "Tap Calls TextView > Tap Call Button > tap Mulong TextView > When you see the video call imagebutton, the task is Almost Completed and STOP THE TASK.",
                          "Tap Send message Button > Tap New contact Textview > Tap SAVE Button > The task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Privacy Textview > when you see Last seen and online TextView, the task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Notifications Textview > Scroll down > Tap Ringtone Textview > when you see on this device TextView, you should mention user to choose ringtone wanted, and the task is Almost Completed and STOP THE TASK.",
                          "Tap the more options ImageView > Tap Settings Textview > Tap Privacy Textview > Scroll down > Tap Blocked contacts Textview > Tap Add Textview > when you see Select contact, you should mention user to choose contact wanted, and the task is Almost Completed and STOP THE TASK.",

                          "Tap New Meeting ImageView > set the team meeting time and start the meeting > when you see Start a meeting button, the task is Almost Completed and STOP THE TASK.",
                          "Tap Join ImageView > the last step is set the team meeting id and join the meeting > when you see Join button, the task is Almost Completed and STOP THE TASK.",
                          "Tap Schedule ImageView > when you see Done Button, you let the user to schedule the meeting,  the task is Almost Completed and STOP THE TASK.",
                          "Tap Share screen ImageView > when you see OK Button, the task is Almost Completed and STOP THE TASK.",
                          "",
                          "",

                          "Tap search bar TextView > search news > Tap news today TextView from list > When you see the video list, the task is Almost Completed and STOP THE TASK.",
                          "Tap search bar TextView > search telstra > Tap telstra TextView > when you see subscribe Button, the task is Almost Completed and STOP THE TASK.",
                          "Tap search bar TextView > search telstra home internet > Scroll down > Tap telstra home internet TextView > When you see the like and dislike button, the task is Almost Completed and STOP THE TASK.",
                          "",
                          "",
                          "",

                          "",
                          "",
                          "",
                          "",
                          "",
                          "",]


        self.__system_prompt_task_match = 'You are an Android mobile assistant, you can only perform the following list of tasks:\n' + str(self.available_task_list) + '\n'\
                                          'Given a user intention, your task is to analyze a user\'s request and match it with up to 3 tasks from the list that most closely align with the user\'s intent.\n' \
                                          '!!!Please respond according to these scenarios:' \
                                          '1. If you find a match, format your response as JSON: {"State": "Match", "RelatedTasks": ["<task from list>"], "Reason": "Provide a concise reason for your choices."}\n' \
                                          '2. If the request is somewhat related but you require further details to refine your match, format your response as JSON: {"State": "Related", "Question": "Pose a clarifying question here.", "Options": ["Option1", "Option2", "..."]}. Ensure the options are directly relevant to the clarifying question, not tasks from the list.\n' \
                                          '3.  If the user\'s request doesn\'t relate to any task on your list, respond with: {"State": "Unrelated"}.\n'

        self.__model_manager = model_manager
        self.__base_prompt_task_match = 'User intention: {task}.'

        self.__system_prompt_app_match = 'You are an Android mobile assistant. ' \
                                         'Given an app list, and an app name needed by a phone user, please select the most relevant app package name from the app list.' \
                                         '!!!Note:\n' \
                                         '1. ONLY use this JSON format to provide your answer: {{"AppPackage": "<selected app package from the app list>", "Reason": "<one-sentence reason for selection>"}}' \
                                         '2. If no app package in the app list directly matches the given app name, select the one that seems most relevant as "AppPackage".' \
                                         '3. The result must contains "AppPackage" key. \n' \
                                         '!!!Example:\n' \
                                         '1. {{"AppPackage": "com.android.settings", "Reason": "The app name Android Settings is related to the app package com.android.settings."}}\n' \
                                         '2. {{"AppPackage": "com.android.camera2", "Reason": "The app name Camera is related to the app package com.android.camera2."}}'
        self.__base_prompt_app_match = 'App list: {app_list}\n App name: {app_name}'

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
            regex = r'"([A-Za-z ]+?)"\s*:\s*(\[[^\]]*\]|\d+|".*?[^\\]"|\'.*?[^\\]\')|\'([A-Za-z ]+?)\'\s*:\s*(\[[^\]]*\]|\d+|\'.*?[^\\]\'|".*?[^\\]")'
            attributes = re.findall(regex, resp['content'])
            resp_dict = {}
            for match in attributes:
                key = match[0].strip('"').strip("'") if match[0] else match[2].strip('"').strip("'")  # Select the correct group for the key
                value = match[1].strip('"').strip("'") if match[1] else match[3].strip('"').strip("'")  # Select the correct group for the value
                resp_dict[key] = value
            return resp_dict

    @staticmethod
    def wrap_task_info(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = ''
        if task.clarification_user_msg is not None and len(task.clarification_user_msg) > 0:
            prompt += '\nUser\'s answer for the last question: ' + task.clarification_user_msg + '.\n'
        return prompt

    def match_task_to_list(self, task):
        """
        Try to find 0-3 related tasks in the available task list for the given user task
        Args:
            task (Task): Task object
        Return:
            task_match (dict): {"RelatedTasks": [] or "None", "Reason":}
        """
        try:
            if len(task.conversation_tasklist) == 0:
                task.conversation_tasklist = [{'role': 'system', 'content': self.__system_prompt_task_match}]
            prompt = self.__base_prompt_task_match.format(task=task.task_description)
            prompt += self.wrap_task_info(task)
            task.conversation_tasklist.append({"role": "user", "content": prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_tasklist)
            task.conversation_tasklist.append(resp)
            task.res_task_match = self.transfer_to_dict(resp)
            task.res_task_match['Proc'] = 'TaskMatch'
            print(task.res_task_match)
            return task.res_task_match
        except Exception as e:
            print(resp)
            raise e

    def match_app_to_applist(self, task, app_list):
        """
        Try to find 0-3 related tasks in the available task list for the given user task
        Args:
            task (Task): Task object
            app_list (list): app lists in user's phone
        Return:
            task_match (dict): {"RelatedTasks": [] or "None", "Reason":}
        """
        try:
            prompt = self.__base_prompt_app_match.format(app_name=task.involved_app, app_list=app_list)
            conversation = [{'role': 'system', 'content': self.__system_prompt_app_match},
                            {"role": "user", "content": prompt}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            app_match = self.transfer_to_dict(resp)
            app_match['Proc'] = 'AppMatch'
            task.involved_app_package = app_match['AppPackage']
            print(app_match)
            return app_match
        except Exception as e:
            print(resp)
            raise e


if __name__ == '__main__':
    task_list = TaskList(None)
