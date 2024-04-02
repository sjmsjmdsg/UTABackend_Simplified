from uta.TaskAction._TaskUIChecker import _TaskUIChecker


class TaskActionChecker:
    def __init__(self, model_manager):
        """
        Initialize TaskActionChecker object.
        """
        self.__model_manager = model_manager
        self.__task_ui_checker = _TaskUIChecker(model_manager)

    @staticmethod
    def action_inquiry(task):
        """
        Execute inquiry type task.
        Args:
            task (Task): Task object containing historical inquiry steps.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM's response.
        """
        try:
            action = {"Action": "Search", "Content": task.task_description}
            task.actions.append(action)
            task.res_action_check = action
            return action
        except Exception as e:
            print('error:', e)
            raise e

    def action_on_ui(self, ui_data, task, printlog=False):
        """
        Check the action in the UI to complete the task
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action":, "Element Id":, "Reason":, "Description":, "Input Text":}
        """
        print('\n*** Check Action on UI *** ')
        # Check ui task relation
        relation = self.__task_ui_checker.check_ui_relation(ui_data, task, printlog)
        task.relations.append(relation)
        return self.wrap_action(action=relation, task=task, ui_data=ui_data)

    def action_on_ui_vision(self, ui_data, task, printlog=False):
        """
        Check the action in the UI to complete the task
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action (dict): {"Action":, "Element Id":, "Reason":, "Description":, "Input Text":}
        """
        # print('\n*** Check Action on UI *** ')
        # Check ui task relation
        relation = self.__task_ui_checker.check_ui_relation_gpt4v(ui_data, task, printlog)
        task.relations.append(relation)
        return self.wrap_action(action=relation, task=task, ui_data=ui_data)

    @staticmethod
    def wrap_action(action, task, ui_data):
        """
        Wrap up action with more attributes retrieved from ui_data
        """
        if task.res_relation_check.get('Element Id') and 'none' not in str(task.res_relation_check['Element Id']).lower():
            try:
                bounds = ui_data.elements[int(action['Element Id'])]['bounds']
                centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
                action['Coordinate'] = centroid
                action['ElementBounds'] = bounds
            except Exception as e:
                print(action)
                raise e
        return action
