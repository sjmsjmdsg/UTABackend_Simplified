from uta.DataStructures._Data import _Data


class Task(_Data):
    def __init__(self, task_id, user_id, task_description=None):
        """
        Initializes a Task instance.
        Args:
            task_id (str): Unique identifier for the task.
            user_id (str): User id associated with the task.
            task_description (str): Description or details of the task.
        """
        super().__init__()
        self.task_id = task_id
        self.user_id = user_id
        self.task_description = task_description
        self.task_type = None       # Type of the task, can be General Inquiry, System Function, or App-Related Task.
        self.cur_package = None     # Current package name (app)
        self.cur_activity = None    # Current activity name (page)

        # Only used when task declaration
        self.conversation_clarification = []  # List of conversations that occurred during multiple turns of task clarification.
        self.conversation_tasklist = []
        self.res_clarification = dict()     # {"Clear": "True", "Question": "None", "Options":[]}
        self.res_justification = dict()
        self.res_classification = dict()    # {"Task Type": "1. General Inquiry", "Explanation":}
        self.res_decomposition = dict()     # {"Decompose": "True", "Sub-tasks":[], "Explanation": }
        self.res_task_match = dict()        # {"RelatedTasks": ["Set up a pin for the device"], "Reason": "The given task is related to device pin."}
        self.selected_task = None           # user selected task
        self.user_clarify = []              # List of string from the user message to further clarify the task
        self.subtasks = []                  # List of string to describe the subtask
        self.involved_app = None            # targeted app for task execution
        self.involved_app_package = None    # targeted app package or task execution
        self.clarification_user_msg = None  # user message for further clarification

        # Only used when task automation
        self.conversation_automation = []   # List of conversations that occurred during multiple turns of task automation.
        self.full_automation_conversation = []  # for testing, store all conversation
        self.res_relation_check = dict()
        self.relations = []                 # List of relations associated with this task.
        self.except_elements_ids = []       # List of except elements that have been tried and proved to be not related to the task
        self.step_hint = None

        # App recommendation
        self.related_app = None             # Related app to complete the task
        self.res_related_app_check = dict()
        self.except_apps = []               # List of except apps that have been proved to be unrelated to the task
