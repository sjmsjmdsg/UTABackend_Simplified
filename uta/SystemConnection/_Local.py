import json
import xmltodict


class _Local:
    def __init__(self):
        pass

    @staticmethod
    def load_xml(file_path, encoding='utf-8'):
        """
        Loads and parses an XML file.
        Args:
            file_path (str): Path to the XML file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed XML content.
        """
        with open(file_path, "r", encoding=encoding) as fp:
            return xmltodict.parse(fp.read())

    @staticmethod
    def load_img(file_path):
        """
        Loads an image file as a binary stream.
        Args:
            file_path (str): Path to the image file.
        Returns:
            Binary content of the image file.
        """
        with open(file_path, "rb") as fp:
            return fp.read()

    @staticmethod
    def load_json(file_path, encoding='utf-8'):
        """
        Loads a JSON file.
        Args:
            file_path (str): Path to the JSON file.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        Returns:
            Parsed JSON data.
        """
        with open(file_path, "r", encoding=encoding) as fp:
            return json.load(fp)

    @staticmethod
    def save_xml(file, file_path, encoding='utf-8'):
        """
        Saves a dictionary as an XML file.
        Args:
            file (dict): Dictionary to save as XML.
            file_path (str): Path where the XML file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        xml_str = xmltodict.unparse(file)
        with open(file_path, "w", encoding=encoding) as fp:
            fp.write(xml_str)

    @staticmethod
    def save_img(img, file_path):
        """
        Saves binary image data to a file.
        Args:
            img (bytes): Binary image data to save.
            file_path (str): Path where the image file will be saved.
        """
        with open(file_path, "wb") as fp:
            fp.write(img)

    @staticmethod
    def save_json(file, file_path, encoding='utf-8'):
        """
        Saves a dictionary as a JSON file.
        Args:
            file (dict): Dictionary to save as JSON.
            file_path (str): Path where the JSON file will be saved.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        with open(file_path, "w", encoding=encoding) as fp:
            json.dump(file, fp, indent=4)
