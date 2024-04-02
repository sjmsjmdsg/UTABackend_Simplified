import openai
import time
import tiktoken
from uta.config import *
import base64
import requests


class _OpenAI:
    def __init__(self, model='gpt-4-1106-preview'):
        """
        Initialize the Model with default settings.
        """
        self.api_key = open(WORK_PATH + 'uta/ModelManagement/OpenAI/openaikey.txt', 'r').readline()
        openai.api_key = self.api_key
        self._model = model

        self.system_prompt = 'You are a mobile virtual assistant that automatically completes a given task on any apps.' \
                             'You understand UIs, analyse the relations between UIs and the given task, and identify the most appropriate elements to proceed or complete the task.' \
                             'You always find the most convenient way to finish the task (e.g., making use of the search bar with flexibility).'

    @staticmethod
    def count_token_size(string, model="gpt-3.5-turbo"):
        """
        Count the token size of a given string to the gpt models.
        Args:
            string (str): String to calculate token size.
            model (str): Using which model for embedding
        Returns:
            int: Token size.
        """
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(string))

    '''
    **********************
    *** Language Model ***
    **********************
    '''
    def send_openai_prompt(self, prompt, system_prompt=None, printlog=False, runtime=True):
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
        if system_prompt is None:
            conversation = [{'role': 'user', 'content': prompt}]
        else:
            conversation = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}]
        return self.send_openai_conversation(conversation=conversation, printlog=printlog, runtime=runtime)

    def send_openai_conversation(self, conversation, printlog=False, runtime=True):
        """
        Send conversation to the llm Model
        Args:
            conversation (list): llm conversation [{'role': 'user', 'content': '...'}, {'role': 'assistant',
            'content':'...'}]
            printlog (bool): True to printout detailed intermediate result of llm
            runtime (bool): True to record the runtime of llm
        Returns:
            message (dict): {'role':'assistant', 'content': '...'}
        """
        try:
            start = time.time()
            if printlog:
                print('*** Asking ***\n', conversation)
            resp = openai.chat.completions.create(model=self._model, messages=conversation, temperature=0.0, seed=42, response_format={"type": "json_object"})
            if runtime:
                usage = resp.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                print(f"[Request cost - ${'{0:.4f}'.format(prompt_tokens / 1000 * 0.01 + completion_tokens / 1000 * 0.03)}] ",
                      f"[Run time - {'{:.3f}s'.format(time.time() - start)}]")
            resp = dict(resp.choices[0].message)
            msg = {'role': resp['role'], 'content': resp['content']}
            if printlog:
                print('\n*** Answer ***\n', msg, '\n')
            return msg
        except Exception as e:
            raise e

    '''
    ********************
    *** Vision Model ***
    ********************
    '''
    def send_gpt4_vision_base64_imgs(self, prompt, base64_imgs, printlog=False):
        """
        Use gpt4-v to analyze base64 images
        Args:
            prompt (str): Prompt to ask questions
            base64_imgs (list): List of base64 image(s)
            printlog (bool): True to printout detailed intermediate result of llm
        Returns:
            success (bool): False to indicate error
            content (string): Response content
        """
        content = [{
                "type": "text",
                "text": prompt
            }]
        for base64_img in base64_imgs:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}",
                    "detail": "high"
                }
            })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {'role': 'system', 'content': self.system_prompt},
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 300,
            "top_p": 0.1,
            "seed": 1
        }
        start = time.time()
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
        if "error" not in response:
            usage = response["usage"]
            prompt_tokens = usage["prompt_tokens"]
            completion_tokens = usage["completion_tokens"]
            if printlog:
                print(f"[Request cost - ${'{0:.4f}'.format(prompt_tokens / 1000 * 0.01 + completion_tokens / 1000 * 0.03)}] ",
                      f"[Run time - {'{:.3f}s'.format(time.time() - start)}]")
        else:
            return False, response["error"]["message"]
        return True, response["choices"][0]["message"]["content"]

    def send_gpt4_vision_img_paths(self, prompt, img_paths, printlog=True):
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
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_imgs = []
        for img_path in img_paths:
            base64_imgs.append(encode_image(img_path))
        return self.send_gpt4_vision_base64_imgs(prompt, base64_imgs, printlog=printlog)


if __name__ == '__main__':
    # llm = _OpenAI(model='gpt-3.5-turbo')
    # llm.send_openai_prompt(prompt='What app can I use to read ebooks?', printlog=True, runtime=True)

    fm = _OpenAI()
    print(fm.send_gpt4_vision_img_paths(prompt='what are in the images?', img_paths=[DATA_PATH + 'user1/task1/0.png']))
