from ppadb.client import Client as AdbClient
import time
import cv2
from os.path import join as pjoin
import os
from uta.config import *


class Device:
    def __init__(self, host='127.0.0.1', port=5037):
        self.__host = host
        self.__port = port
        self.__adb_device = None

    def connect(self):
        """
        Connects to the first device found on the ADB server.
        """
        if self.__adb_device is None:
            self.__adb_device = AdbClient(host=self.__host, port=self.__port).devices()[0]
            print('=== Load Device - ' + self.get_device_name() + '-' + str(self.get_device_resolution()) + ' ===')
        else:
            # Raise an error if a device connection already exists
            raise Exception("Device has already been connected.")

    def is_connected(self):
        """
        Check whether the ADB device is connected.
        """
        if self.__adb_device is None:
            return False
        else:
            return True

    def disconnect(self):
        """
        Disconnects from the ADB device if a connection exists.
        """
        if self.__adb_device is not None:
            self.__adb_device = None

    '''
    ***********************
    *** Collect UI Data ***
    ***********************
    '''
    def cap_and_save_ui_screenshot_and_xml(self, ui_id, output_dir):
        """
        Capture and save ui screenshot and xml to target directory
        Args:
            ui_id (int or string): The id of the current ui, used to name the saved files
            output_dir (path): Directory to save img and xml
        Returns:
            screen_path, xml_path
        """
        os.makedirs(output_dir, exist_ok=True)
        screen_path = pjoin(output_dir, str(ui_id) + '.png')
        xml_path = pjoin(output_dir, str(ui_id) + '.xml')
        screen = self.cap_screenshot()
        with open(screen_path, 'wb') as fp:
            fp.write(screen)
        xml = self.cap_current_ui_hierarchy_xml()
        with open(xml_path, 'w', encoding='utf-8') as fp:
            fp.write(xml)
        # print('- Export UI image and xml to ', screen_path, xml_path, '-')
        return screen_path, xml_path

    def cap_screenshot(self, recur_time=0):
        """
        Captures a screenshot of the current device screen.
        Args:
            recur_time (int): A counter for recursion, to retry capturing the screenshot, must be in [0, 3).
        Returns:
            Binary data of the captured screenshot.
        """
        print('* Capture screenshot *')
        assert 0 <= recur_time < 3
        screen = self.__adb_device.screencap()
        if recur_time and screen is None:
            screen = self.cap_screenshot(recur_time-1)
        return screen

    def cap_current_ui_hierarchy_xml(self):
        """
        Captures the current UI hierarchy of the device screen.
        Returns:
            XML content representing the UI hierarchy.
        """
        # Send the command to dump the UI hierarchy to an XML file on the device
        self.__adb_device.shell('uiautomator dump')

        # Read the content of the dumped XML file directly from the device
        xml_content = self.__adb_device.shell('cat /sdcard/window_dump.xml')
        return xml_content

    '''
    ***********
    *** App ***
    ***********
    '''

    def reboot_app(self, package_name, waiting_time=3):
        """
        Reboots an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to reboot.
            waiting_time (int): Time to wait after launching the app, in seconds.
        """
        print('--- Rebooting app:', package_name, '---')
        # Step 1: Force stop the app
        self.close_app(package_name, waiting_time)

        # Step 2: Launch the app using the existing launch_app method
        self.launch_app(package_name, waiting_time)

    def launch_app(self, package_name, waiting_time=3):
        """
        Launches an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to launch.
            waiting_time (int): Time to wait after launching the app, in seconds.
        """
        print('--- Launch app:', package_name, '---')
        self.__adb_device.shell(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')
        time.sleep(waiting_time)

    def close_app(self, package_name, waiting_time=3):
        """
        Force stops an app on the device by its package name.
        Args:
            package_name (str): The package name of the app to close.
            waiting_time (int): Time to wait after closing the app, in seconds.
        """
        print('--- Close app:', package_name, '---')
        self.__adb_device.shell(f'am force-stop {package_name}')
        time.sleep(waiting_time)

    def get_app_list_on_the_device(self):
        """
        Retrieves a list of all installed applications on the device.
        Returns:
            A list of package names of the installed applications.
        """
        packages = self.__adb_device.shell('pm list packages')
        package_list = packages.split('\n')
        return [p.replace('package:', '') for p in package_list]

    def get_current_package_and_activity_name(self):
        """
        Retrieves the current foreground package and activity name.
        Returns:
            A dictionary with 'package_name' and 'activity_name'.
        """
        dumpsys_output = self.__adb_device.shell('dumpsys activity activities | grep ResumedActivity')
        package_and_activity = dumpsys_output.split('u0 ')[1].split('}')[0]
        package_name, activity_name = package_and_activity.split('/')
        print('Package name:', package_name, 'Activity name:', activity_name)
        return package_name, activity_name

    '''
    ***********************
    *** Get Device Info ***
    ***********************
    '''
    def check_keyboard_active(self):
        """
        Checks if the keyboard is active (visible) on the device.
        Returns:
            True if the keyboard is visible, False otherwise.
        """
        dumpsys_output = self.__adb_device.shell('dumpsys input_method | grep mInputShown')
        if 'mInputShown=true' in dumpsys_output:
            return True
        return False

    def get_device(self):
        """
        Retrieves the current ADB device object.
        Returns:
            The ADB device object.
        """
        return self.__adb_device

    def get_device_name(self):
        """
        Retrieves the serial number of the connected device.
        Returns:
            The serial number of the device.
        """
        return self.__adb_device.get_serial_no()

    def get_device_resolution(self):
        """
        Retrieves the screen resolution of the connected device.
        Returns:
            The screen resolution as a tuple (width, height).
        """
        return tuple(self.__adb_device.wm_size())

    '''
    ***************
    *** Actions ***
    ***************
    '''
    def take_action(self, action, ui_data, show=False):
        """
        Take action on the device
        Args:
            action (dict): {"Action":, "Coordinate":, "Element Id":, "Input Text":, "Description":, "Reason":}
            ui_data (UIData): UI data containing the element coordinates
            show (bool): If True, displays the annotated action
        """
        print('* Perform Action *')
        action_type = action['Action'].lower()
        if 'click' in action_type:
            return self.click_screen(ui_data, int(action['Element Id']), show)
        elif 'scroll' in action_type:
            return self.up_scroll_screen(ui_data, int(action['Element Id']), show)  # scroll down
        elif 'swipe' in action_type:
            return self.left_swipe_screen(ui_data, int(action['Element Id']), show)
        elif 'input' in action_type:
            return self.input_text(action['Input Text'], ui_data, int(action['Element Id']))
        elif 'launch' in action_type:
            return self.launch_app(action['App'])
        elif 'back' in action_type:
            return self.go_back()
        else:
            raise ValueError(f"No expected action returned from model, returned action: {action_type}")

    def click_screen(self, ui, element_id, show=False):
        """
        Simulates a tap on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to tap.
            show (bool): If True, displays the tap visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        self.__adb_device.input_tap(centroid[0], centroid[1])
        if show:
            return self.mark_circle_on_element_centroid(centroid, ui.ui_screenshot.copy())

    def long_press_screen(self, ui, element_id, show=False):
        """
        Simulates a long press on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to long press.
            show (bool): If True, displays the long press visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        self.__adb_device.input_swipe(centroid[0], centroid[1], centroid[0], centroid[1], 3000)
        if show:
            return self.mark_circle_on_element_centroid(centroid, ui.ui_screenshot.copy())

    def up_scroll_screen(self, ui, element_id, show=False):
        """
        Simulates an upward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to scroll up.
            show (bool): If True, displays the scroll action visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        scroll_start = ((bounds[2] + bounds[0]) // 2, 2000)
        scroll_end = ((bounds[2] + bounds[0]) // 2, 100)
        self.__adb_device.input_swipe(scroll_start[0], scroll_start[1], scroll_end[0], scroll_end[1], 500)
        if show:
            return self.mark_arrow_for_scroll(scroll_start, scroll_end, ui.ui_screenshot.copy())

    def down_scroll_screen(self, ui, element_id, show=False):
        """
        Simulates a downward scroll on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to scroll down.
            show (bool): If True, displays the scroll action visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[3])
        scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        self.__adb_device.input_swipe(scroll_start[0], scroll_start[1], scroll_end[0], scroll_end[1], 500)
        if show:
            return self.mark_arrow_for_scroll(scroll_start, scroll_end, ui.ui_screenshot.copy())

    def right_swipe_screen(self, ui, element_id, show=False):
        """
        Simulates a right swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to swipe right.
            show (bool): If True, displays the swipe action visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        bias = 20
        swipe_start = (bounds[0] + bias, (bounds[3] + bounds[1]) // 2)
        swipe_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
        self.__adb_device.input_swipe(swipe_start[0], swipe_start[1], swipe_end[0], swipe_end[1], 500)
        if show:
            return self.mark_arrow_for_scroll(swipe_start, swipe_end, ui.ui_screenshot.copy())

    def left_swipe_screen(self, ui, element_id, show=False):
        """
        Simulates a left swipe on a specified element of the UI.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to swipe left.
            show (bool): If True, displays the swipe action visually.
        """
        ele = ui.elements[element_id]
        bounds = ele['bounds']
        bias = 20
        swipe_start = (bounds[2] - bias, (bounds[3] + bounds[1]) // 2)
        swipe_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
        self.__adb_device.input_swipe(swipe_start[0], swipe_start[1], swipe_end[0], swipe_end[1], 500)
        if show:
            return self.mark_arrow_for_scroll(swipe_start, swipe_end, ui.ui_screenshot.copy())

    def input_text(self, text, ui, element_id):
        """
        Inputs text into the currently focused field on the device.
        Args:
            ui: UI object containing elements.
            element_id: The id for the element in the UI to tap.
            text (str): The text to input.
        """
        self.click_screen(ui, element_id)  # Click to activate the keyboard and update the element.
        self.__adb_device.input_text(text)
        self.__adb_device.shell('input keyevent 66')  # Simulate pressing the Enter key.


    def go_back(self, waiting_time=2):
        """
        Simulates the 'Back' button press on the device.
        Args:
            waiting_time (int): Time to wait after the action, in seconds.
        """
        self.__adb_device.shell('input keyevent KEYCODE_BACK')
        # wait a few second to be refreshed
        time.sleep(waiting_time)

    def go_homepage(self, waiting_time=3):
        """
        Simulates the "Go Home Page" operation.
        Args:
            waiting_time (int): Time to wait after the action, in seconds.
        """
        self.__adb_device.shell('input keyevent KEYCODE_HOME')
        # wait a few second to be refreshed
        time.sleep(waiting_time)

    '''
    ***************
    *** Utils ***
    ***************
    '''
    @staticmethod
    def mark_circle_on_element_centroid(centroid, board):
        """
        Mark a circle on the target element centroid
        Args:
            centroid (tuple): coord of centroid of the element
            board (img): image to be drawn
        """
        cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
        cv2.imshow('tar element', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('tar element')
        return board

    @staticmethod
    def mark_arrow_for_scroll(scroll_start, scroll_end, board):
        """
        Show arrow for the scroll
        Args:
            scroll_start (tuple): start point
            scroll_end (tuple): end point
            board (img): image to be drawn
        """
        cv2.arrowedLine(board, scroll_start, scroll_end, (255, 0, 255), 8)
        cv2.imshow('scroll', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
        cv2.waitKey()
        cv2.destroyWindow('scroll')
        return board


if __name__ == '__main__':
    device = Device()
    device.connect()
    device.get_app_list_on_the_device()
    device.cap_and_save_ui_screenshot_and_xml(1, WORK_PATH + 'data/device')
