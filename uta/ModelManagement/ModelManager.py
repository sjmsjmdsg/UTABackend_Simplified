from uta.ModelManagement.OpenAI import _OpenAI
from uta.ModelManagement.GoogleOCR import _GoogleOCR
# from uta.ModelManagement.IconCls import _IconClassifier


class ModelManager:
    def __init__(self):
        """
        Initializes a ModelManager instance with vision model and fm model.
        """
        self.__fm_model = _OpenAI()
        self.__google_ocr = _GoogleOCR()
        # self.__icon_cls = _IconClassifier()

    '''
    ********************
    *** Vision Model ***
    ********************
    '''
    def detect_text_ocr(self, img_path):
        """
        Sends an OCR request to the Google Cloud Vision API.
        Args:
            img_path (str): Image file path.
        Returns:
            The detected text annotations or None if no text is found.
        """
        return self.__google_ocr.detect_text_ocr(img_path)

    def classify_icons(self, imgs):
        """
        Predict the class of the given icons images.
        Args:
            imgs (list): List of images in numpy array format.
        Returns:
            List of predictions with class names and probabilities.
        """
        return self.__icon_cls.classify_icons(imgs)

    '''
    ****************************
    *** Large Language Model ***
    ****************************
    '''
    @staticmethod
    def count_token_size(string, model='gpt-3.5-turbo'):
        """
        Count the token size of a given string to the gpt models.
        Args:
            string (str): String to calculate token size.
            model (str): Using which model for embedding
        Returns:
            int: Token size.
        """
        return _OpenAI().count_token_size(string, model=model)

    def send_fm_prompt(self, prompt, system_prompt=None, printlog=False, runtime=True):
        """
        Send single prompt to the llm Model
        Args:
            system_prompt (str) : system role setting
            prompt (str): Single prompt
            printlog (bool): True to printout detailed intermediate result of llm
            runtime (bool): True to record the runtime of llm
        Returns:
            message (dict): {'role':'assistant', 'content': '...'}
        """
        return self.__fm_model.send_openai_prompt(prompt=prompt, system_prompt=system_prompt, printlog=printlog, runtime=runtime)

    def send_fm_conversation(self, conversation, printlog=False, runtime=False):
        """
        Send conversation to the llm Model.
        Args:
            conversation (list): llm conversation [{'role': 'user', 'content': '...'}, {'role': 'assistant',
            'content':'...'}]
            printlog (bool): True to printout detailed intermediate result of llm
            runtime (bool): True to record the runtime of llm
        Returns:
            message (dict): {'role':'assistant', 'content': '...'}
        """
        return self.__fm_model.send_openai_conversation(conversation=conversation, printlog=printlog, runtime=runtime)

    '''
    **************************
    *** Large Vision Model ***
    **************************
    '''
    def send_gpt4_vision_img_paths(self, prompt, img_paths, printlog=False):
        """
        Read images as base64 and use gpt4-v to analyze images
        Args:
            prompt (str): Prompt to ask questions
            img_paths (list of paths): List of image file path(s)
            printlog (bool): True to printout detailed intermediate result of llm
        Returns:
            success (bool): False to indicate error
            content (string): Response content
        """
        return self.__fm_model.send_gpt4_vision_img_paths(prompt=prompt, img_paths=img_paths, printlog=printlog)


if __name__ == '__main__':
    model_mg = ModelManager()
    model_mg.send_fm_prompt(prompt='How are you', system_prompt='You are an assistant')
