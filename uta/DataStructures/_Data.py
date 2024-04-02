class _Data:
    def __init__(self):
        pass

    def to_dict(self):
        """
        Returns a dictionary representation of the AutonomicTask instance.
        """
        return {k: v for k, v in self.__dict__.items()}

    def load_from_dict(self, dict_data):
        """
        Set attributes values by the given dict_obj
        Args:
            dict_data (dict): The dict with attributes and values
        """
        for key, value in dict_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_attributes(self, **kwargs):
        """
        Dynamically sets attributes based on provided keyword arguments.
        Args:
            **kwargs: Key-value pairs to set as attributes.
        Raises:
            AttributeError: If a given attribute is not defined in the class.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")
