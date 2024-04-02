import json
import re


class _UIChecker:
    """
    Check the special content and state of the UI
    """
    def __init__(self, model_manager):
        self.__model_manager = model_manager
        self.__system_prompt = 'You are a mobile assistant. Given an UI, you should check if it contains any of the following components that require user decisions:\n' \
                               '1. UI Modal: A window or dialog box overlaying on the top of main content showing Alerts, Confirmations or Instructions.\n' \
                               '2. User Permission: Dialog box asking for user permission to perform app functionalities.\n' \
                               '3. Login Page: Requiring for account login before using app.\n' \
                               '4. Form: Requiring user to fill in private data.\n' \
                               '!!!Respond to the following points:\n' \
                               '1. "Component": if the UI contains any of the given components, if not, answer "None".\n' \
                               '2. "Explanation": one-sentence explanation of your decision. \n' \
                               '3. "Required action": required action for the user to proceed (e.g., dismiss the box, allow permission, fill in info)' \
                               '!!!Note:\n' \
                               '1. ONLY use this JSON format to provide your answer: {{"Component": "<Component>", "Explanation": "<Explanation>", "Required action": "<Required action"}}\n' \
                               '2. Do not include EditText for search settings.\n' \
                               '!!!Example:\n' \
                               '1. {{"Component": "User Permission", "Explanation": "This UI asks user permission to access photo", "Required action": "Allow or deny the permission"}}\n' \
                               '2. {{"Component": "None", "Explanation": "No mentioned components in this UI"}}\n'

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

    def check_ui_decision_page(self, ui_data):
        """
        Check if the UI contain any following special components that require user intervention:
        1. UI Modal; 2. User Permission; 3. Login; 4. Form;
        Args:
            ui_data (UIData)
        Returns:
            response (dict): {"Component", "Explanation"}
        """
        try:
            conversation = [{'role': 'system', 'content': self.__system_prompt},
                            {'role': 'user', 'content': f'Here is the view hierarchy of a UI :\n'
                                                        f'{str(ui_data.element_tree)}\n'}]
            resp = self.__model_manager.send_fm_conversation(conversation)
            special_compo = self.transfer_to_dict(resp)
            print(special_compo)
            return special_compo
        except Exception as e:
            print(resp)
            raise e
