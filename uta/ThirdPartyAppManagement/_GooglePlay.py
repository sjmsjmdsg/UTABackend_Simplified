import time
import requests
from bs4 import BeautifulSoup
import re
from google_play_scraper import app, search


class _GooglePlay:
    def __init__(self):
        """
        Initializes the GooglePlay class.
        Sets up the base URL for searching apps on the Google Play store.
        """
        self.__search_url = 'https://play.google.com/store/search?q={app_name}&c=apps'

    def search_app_by_name(self, app_name):
        """
        Searches for an app by its name on the Google Play store.
        Args:
            app_name (str): The name of the app to search for.
        Returns:
            The most relevant app's information if found, otherwise None.
        """
        try:
            start = time.time()
            # crawl the google play website
            response = requests.get(self.__search_url.replace('{app_name}', app_name))
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # scrape the most related app
            elements = soup.find_all(class_='Qfxief')
            if elements and len(elements) > 0:
                element = elements[0]
            else:
                print('No exact app find by the name')
                return None
            # get the appId through href
            app_id = re.search(r'id=([^ ]+)', element['href'])
            if app_id:
                tar_app = app(app_id.group(1))
                print('Running Time:%.3fs, ' % (time.time() - start),
                      'Fetched APP: {App id:', tar_app['appId'], '} {App title:', tar_app['title'], '}')
                return tar_app
            else:
                print("No match found!")
                return None
        except Exception as e:
            raise e
        
    @staticmethod
    def search_apps_fuzzy(disp):
        """
        Performs a fuzzy search for apps on the Google Play store.
        Args:
            disp (str): The display term to search for.
        Returns:
            A list of apps that are related to the search term.
        """
        try:
            result = search(disp)
            print('Number of related apps:', len(result))
            for res in result:
                print(res['appId'], res['title'])
            return result
        except Exception as e:
            raise e
