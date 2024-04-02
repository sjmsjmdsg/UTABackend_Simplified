from uta.DataStructures._Data import _Data


class User(_Data):
    def __init__(self, user_id, device_resolution=(1080, 2280), app_list=None):
        """
        Initializes a _User instance.
        Args:
            user_id (str): Identifier for the user.
            device_resolution (tuple): Specify the size/resolution of the UI
            app_list (list): List of the names of installed apps
        """
        super().__init__()
        self.user_id = user_id
        self.device_resolution = device_resolution
        self.app_list = app_list
