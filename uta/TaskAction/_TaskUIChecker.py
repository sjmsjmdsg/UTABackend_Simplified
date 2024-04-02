from uta.config import *
import json
import re


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__relation_prompt = 'What is the relation between this UI and the task "{task}" and why?\n' \
                                 '!!!Relation Options:\n'\
                                 '1. Almost Complete: The UI is at the final stage, with only one action left to complete the task. This status applies if the next action directly concludes the task (e.g., finalizing a setting adjustment).\n' \
                                 '2. Directly related: The UI contains elements (clickable, scrollable, swipeable) that are essential for advancing the task, but it isn\'t the task\'s final step.\n' \
                                 '3. Indirectly related: Although the UI doesn\'t have direct elements for the task, it includes elements that lead to the relevant UI or task (e.g., a settings button, search bar).\n' \
                                 '4. Unrelated: The UI is irrelevant to the task or any sub-tasks.\n' \
                                 '!!!Notes:\n' \
                                 '- For Almost Complete, include the element ID for the final action and a brief reason.\n' \
                                 '- For Directly or Indirectly Related, check if the UI contains:\n' \
                                 '-- UI Modal: Overlay windows (e.g., alerts, confirmations).\n' \
                                 '-- User Permission: Permissions request dialogs.\n' \
                                 '-- Login Page: Login requirements.\n' \
                                 '-- Form: Personal data input forms.\n' \
                                 '-- If present, describe the component, provide a reason, and specify the user\'s required action.\n' \
                                 '- For Unrelated scenarios, try to find which element in the current UI can be clicked to navigate back or close the current unrelated UI to proceed the task, suggest "Back" as the action.\n\n' \
                                 'Response Format:\n' \
                                 '1. If Almost Complete, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>"}}\n' \
                                 '2. If Directly or Indirectly Related and components are present, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Component": "<component>", "Explanation": "<explanation>", "Required action": "<action>"}}\n' \
                                 '3. If Directly or Indirectly Related without specific components, specify the action to proceed (Click, Input, Scroll, Swipe) and, if applicable, the input text:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Action": "<type>", "Input Text": "<text>"}}\n' \
                                 '4. If Unrelated, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID or None>", "Reason": "<reason>", "Action": "Back"}}\n\n' \
                                 'Examples:\n' \
                                 '- Indirectly Related with User Permission Component:\n' \
                                 '{{"Relation": "Indirectly related", "Element Id": "2", "Reason": "The UI has a search bar to find \'Turn on voice\'", "Component": "User Permission", "Explanation": "Asks for photo access permission", "Required action": "Allow or deny"}}\n' \
                                 '- Directly Related with Action:\n' \
                                 '{{"Relation": "Directly related", "Element Id": "3", "Reason": "UI has \'Open Settings\' for task settings access", "Action": "Click"}}\n' \
                                 '- Unrelated with Back Action:\n' \
                                 '{{"Relation": "Unrelated", "Element Id": "3", "Reason": "This element enables returning to the last page.", "Action": "Back"}}\n\n' \
                                 '!!!Additional Notes:\n' \
                                 '1. If the UI indicates the task has nearly reached completion (requiring just one final user action), select "Almost Complete".\n' \
                                 '2. Delete all the words in searching bar before start a new search trying.\n' \
                                 '3. Do NOT try to repeat previous actions as they have been tried.\n' \
                                 '4. If the relation is related/almost complete, give the Element Id (int) of the related element\n' \
                                 '5. If Relation is almost complete, you must provide the Element Id (int) required for the final step and describe its operation in the Reason.\n' \
                                 '6. If you decide to input text, the Action should be Input.'

        self.__relation_prompt_gpt4v = 'Analyze the relationship between the provided UI and the specified task "{task}" to determine the relations and actions for proceeding with the task.\n' \
                                       '!!!Relations Options:\n' \
                                       '1.	Complete:  If the task has been completed or only requires user\'s input to complete the task, mark as Complete. This includes situations where user input or a sensitive decision is the last step to finalize the task.\n' \
                                       'a.	Output Format: {{"Relation": "Complete", "Reason": <reason>, "UI Desc": <UI Description>}}.\n' \
                                       'b.  Note:\n' \
                                       '-   If you cannot confirm whether the page requiring user decision is the final page and no further actions are required beyond this input, give "Complete".\n' \
                                       '2.	Related: The UI contains elements (clickable, scrollable, swipeable) that are essential for moving the task forward but isn\'t at the final step.\n' \
                                       'a.	Output Format: {{"Relation": "Related", "Element Id": <ID>, "Reason": <reason>, "Action": <type>, "Action Desc": <Action Description>, "UI Desc": <UI Description>, "Input Text": <text>}}\n' \
                                       'b.	Note:\n' \
                                       '-	Action types: Click, Input, Scroll, Swipe.\n' \
                                       '-	If the action type is Input, output text content to "Input Text", otherwise output "None" to "Input Text", output the element id of the textfield.\n' \
                                       '-	This UI may not contain the directly related elements for the task, but it may include elements that lead to the relevant UI (e.g., menu button, tabs, search bar, setting buttons)\n' \
                                       '-   Describe your action in one sentence in "Action Desc".\n' \
                                       '3.	Unrelated: The UI is completely irrelevant to the task, without even indirectly related elements.\n' \
                                       'a.	Output Format: {{"Relation": "Unrelated", "Reason": <reason>, "UI Desc": <UI Description>, "Action": "Back", "Element Id": <ID>}}\n' \
                                       'b.	Note:\n' \
                                       '-   Identify elements for navigating back or closing the UI to proceed to a related UI, if non-applicable, give "None" as Element Id.\n' \
                                       '-   Always give "Back" as Action.\n' \
                                       '4.	User Action Required: The UI requires specific user input or choice that cannot be determined programmatically, under the defined Interaction Paradigm, and this input is not a sensitive information (e.g., which fruit to choose in a shop app).\n' \
                                       'a.	Output Format: {{"Relation": "User Action Required", "Interaction Paradigm": <Paradigm shown in UI>, "Reason": <reason>, "UI Desc": <UI Description>}}\n' \
                                       'b.	Note:\n' \
                                       '-   Type of Interaction Paradigm: Lists and Menus, Grids and Cards, Sliders and Steppers, Calendars and Date Pickers, Dialogs and Toasts, Forms and Text Fields, Gesture/Sound-based Interactions, Customization and Personalization Panels, Interactive Maps and Location Pickers\n' \
                                       '-   Use this action when the task involves non-sensitive decisions that require user preference or input, and there are no clear instructions that can be inducted from the given task.\n' \
                                       '-   Only apply this action if the UI is NOT on the final page/requires user\'s final input to complete the task.\n' \
                                       '5.  Sensitive Action: The UI relates to sensitive actions or information that necessitates direct user involvement.\n' \
                                       'a.  Output Format: {{"Relation": "Sensitive Action", "Reason": <reason>, "UI Desc": <UI Description>}}\n' \
                                       'b. Note:\n' \
                                       '-   Apply this action for tasks involving sensitive information or decisions, such as money-related behaviors, private information input, permission grants, etc. This action should be chosen if the task description indicates the user’s clear intent but involves sensitive actions that the model cannot autonomously decide on.\n' \
                                       '-   Only apply this action if the UI is NOT on the final page/requires user\'s final input to complete the task.\n' \
                                       '!!!Examples:\n' \
                                       '{{"Relation": "Complete", "Reason": "The UI is on the \'New contact\' screen which is the final step to add a new contact in WhatsApp.", "UI Desc": "A UI of the WhatsApp contact list with an option to add a new contact."}}\n' \
                                       '{{"Relation": "Related", "Element Id": 3, "Reason": "UI has \'Open Settings\' for task settings access", "Action": "Click", "Action Desc": "Click on the Setting button to open setting."}}\n' \
                                       '{{"Relation": "Unrelated", "Element Id": 3, "Reason": "This element enables returning to the last page.", "Action": "Back"}}\n' \
                                       '{{"Relation": "User Action Required", "Interaction Paradigm": "Lists and Menus", "Reason": "The task does not clearly state which video to choose", "UI Desc": "A UI of list of videos of the Youtube."}}\n' \
                                       '{{"Relation": "Sensitive Action", "Reason": "The task does not clearly state which video to choose", "UI Desc": "A UI of list of videos of the Youtube."}}\n' \
                                       '!!!Instructions:\n' \
                                       '1.	Refer to UI elements by their bounding box annotations and IDs (int) in the UI image.\n' \
                                       '2.	Respond ONLY in JSON format compatible with python json.loads, including all required attributes.\n' \
                                       '3.	Provide a one-sentence description for the current UI in the "UI Desc”.\n' \
                                       '4.	Provide a one-sentence reason for your answer in the "Reason".\n' \
                                       '5.	Ensure all required attributes are included in your JSON response.\n' \
                                       '6.  Always consider the current state of the UI and the history of actions taken to ensure responses adapt to the task\'s progression without repetition. Adjustments to action suggestions should be made based on the latest UI context.'


    '''
    **************
    *** Basics ***
    **************
    '''
    @staticmethod
    def wrap_task_context(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = '!!!Context:\n'
        prompt += 'Keyboard active: ' + str(task.keyboard_active) + '.\n'
        # if task.step_hint is not None:
        #     prompt += "(Additional step hints to proceed the task:" + str(task.step_hint) + ')\n'
        # if len(task.user_clarify) > 0:
        #     prompt += '(Additional information and commands for the task:' + str(task.user_clarify) + ')\n'
        # if len(task.subtasks) > 0:
        #     prompt += '(Potential subtasks and steps to complete the task: ' + str(task.subtasks) + '.)\n'
        return prompt

    @staticmethod
    def wrap_task_history(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = ''
        if len(task.relations) > 0:
            prompt += '!!!Action history for this task - MUST NOT REPEAT PREVIOUS ACTIONS:\n ' + str(task.relations) + '.\n'
        return prompt

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
            return_json = json.loads(resp['content'])
            return return_json
        except Exception as e:
            regex = r'"([A-Za-z ]+?)"\s*:\s*(\[[^\]]*\]|\d+|".*?[^\\]"|\'.*?[^\\]\')|\'([A-Za-z ]+?)\'\s*:\s*(\[[^\]]*\]|\d+|\'.*?[^\\]\'|".*?[^\\]")'
            attributes = re.findall(regex, resp['content'])
            resp_dict = {}
            for match in attributes:
                key = match[0].strip('"').strip("'") if match[0] else match[2].strip('"').strip("'")  # Select the correct group for the key
                value = match[1].strip('"').strip("'") if match[1] else match[3].strip('"').strip("'")  # Select the correct group for the value
                resp_dict[key] = value
            return resp_dict

    def check_ui_task(self, ui_data, task, prompt, printlog=False):
        """
        Check UI and Task by prompt through foundation model
        """
        try:
            if len(task.conversation_automation) == 0:
                task.conversation_automation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                {'role': 'user', 'content': f'This is a view hierarchy of a UI:\n'
                                                                            f'{str(ui_data.element_tree)}\n\n{prompt}'}]
                task.full_automation_conversation += [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                      {'role': 'user', 'content': f'This is a view hierarchy of a UI:\n'
                                                      f'{str(ui_data.element_tree)}\n\n{prompt}'}]
            else:
                task.conversation_automation.append({'role': 'user', 'content': prompt})
                task.full_automation_conversation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            task.full_automation_conversation.append(resp)
            return resp
        except Exception as e:
            print(resp)
            raise e

    def check_ui_task_gpt4v(self, ui_data, task, prompt, printlog=False):
        """
        Check UI and Task by prompt through foundation gpt4v model
        """
        try:
            task.conversation_automation.append({'role': 'user', 'content': prompt})
            task.full_automation_conversation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_gpt4_vision_img_paths(prompt=prompt, img_paths=[ui_data.annotated_elements_screenshot_path], printlog=printlog)
            resp = {'role': 'assistant', 'content': resp[1]}
            task.conversation_automation.append(resp)
            task.full_automation_conversation.append(resp)
            return resp
        except Exception as e:
            print(resp)
            raise e

    '''
    *********************
    *** Task-UI Check ***
    *********************
    '''
    def check_ui_relation(self, ui_data, task, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Relation":, "Reason":}
        """
        try:
            print('* Check UI and Task Relation *')
            # Format base prompt
            prompt = self.wrap_task_context(task)
            prompt += self.wrap_task_history(task)
            prompt += self.__relation_prompt.format(task=task.selected_task)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_relation_check = self.transfer_to_dict(resp)
            print(task.res_relation_check)
            return task.res_relation_check
        except Exception as e:
            print(resp)
            raise e

    def check_ui_relation_gpt4v(self, ui_data, task, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Relation":, "Reason":}
        """
        try:
            print('* Check UI and Task Relation *')
            # Format base prompt
            # prompt = self.wrap_task_context(task)
            prompt = self.wrap_task_history(task)
            prompt += self.__relation_prompt_gpt4v.format(task=task.selected_task)
            # Ask FM
            resp = self.check_ui_task_gpt4v(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            print('resp:\n', resp)
            task.res_relation_check = self.transfer_to_dict(resp)
            # print('transferred:\n', task.res_relation_check)
            # print(task.res_relation_check)
            return task.res_relation_check
        except Exception as e:
            print(resp)
            raise e