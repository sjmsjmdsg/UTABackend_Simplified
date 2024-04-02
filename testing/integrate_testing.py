from os.path import join as pjoin
import os
import cv2
import traceback
import time

from testing.Device import Device
from testing.data_util import *
from uta.UTA import UTA
from uta.config import *
from uta.SystemConnection import SystemConnector


def annotate_ui_operation(ui, recommended_action, show=False):
    """
    Create annotated UI for debugging
    """
    assert recommended_action != "None"

    try:
        ele = ui.elements[int(recommended_action["Element Id"])]
        bounds = ele['bounds']
        action_type = recommended_action['Action'].lower()

        if 'click' in action_type:
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            annotated_screenshot = board
        elif 'press' in action_type:
            centroid = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, (centroid[0], centroid[1]), 20, (255, 0, 255), 8)
            annotated_screenshot = board
        # elif 'scroll up' in action_type:
        #     scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
        #     scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[1])
        #     board = ui.ui_screenshot.copy()
        #     cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
        #     cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
        #     annotated_screenshot = board
        elif 'scroll' in action_type:
            # scroll_end = ((bounds[2] + bounds[0]) // 2, bounds[3])
            # scroll_start = ((bounds[2] + bounds[0]) // 2, (bounds[3] + bounds[1]) // 2)
            scroll_end = ((bounds[2] + bounds[0]) // 2, 2000)
            scroll_start = ((bounds[2] + bounds[0]) // 2, 100)
            board = ui.ui_screenshot.copy()
            cv2.circle(board, scroll_start, 20, (255, 0, 255), 8)
            cv2.circle(board, scroll_end, 20, (255, 0, 255), 8)
            annotated_screenshot = board
        # elif 'swipe right' in action_type:
        #     bias = 20
        #     swipe_start = (bounds[0] + bias, (bounds[3] + bounds[1]) // 2)
        #     swipe_end = (bounds[2], (bounds[3] + bounds[1]) // 2)
        #     board = ui.ui_screenshot.copy()
        #     cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
        #     annotated_screenshot = board
        elif 'swipe' in action_type:
            bias = 20
            swipe_start = (bounds[2] - bias, (bounds[3] + bounds[1]) // 2)
            swipe_end = (bounds[0], (bounds[3] + bounds[1]) // 2)
            board = ui.ui_screenshot.copy()
            cv2.arrowedLine(board, swipe_start, swipe_end, (255, 0, 255), 8)
            annotated_screenshot = board
        elif 'input' in action_type:
            text = recommended_action['Input Text']
            text_x = bounds[0] + 5  # Slightly right from the left bound
            text_y = (bounds[1] + bounds[3]) // 2  # Vertically centered
            board = ui.ui_screenshot.copy()
            cv2.putText(board, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            annotated_screenshot = board
        else:
            annotated_screenshot = ui.ui_screenshot.copy()
    except Exception as e:
        print(e)
        annotated_screenshot = ui.ui_screenshot.copy()
    if show:
        cv2.imshow('a', cv2.resize(annotated_screenshot, (500, 1000)))
        cv2.waitKey()
        cv2.destroyAllWindows()
    _, encoded_image = cv2.imencode('.png', annotated_screenshot)
    return encoded_image.tobytes()


def task_declaration(msg, max_try=20):
    for i in range(max_try):
        try:
            dec = uta.declare_task(user_id=user_id, task_id=task_id, user_msg=msg)

            if dec.get("Action") is not None and dec["Action"] == "Error at the backend.":
                save_error(dec["Exception"], dec["Traceback"], "declaration_error")
                break

            if dec.get('AppPackage'):
                break

            if dec.get('State') and 'related' in dec['State'].lower() or \
                    dec.get('State') is None and 'related' in str(dec).lower():
                print(dec)
                msg = input('Input your answer:')
            elif (dec.get('State') and 'unrelated' in dec['State'].lower() or
                  dec.get('State') is None and 'unrelated' in str(dec).lower()):
                print(dec)
                msg = input('Input your Task:')
            elif (dec.get('State') and 'match' in dec['State'].lower() or
                     dec.get('State') is None and 'match' in str(dec).lower()):
                print(dec)
                msg = dec["RelatedTasks"][0]
                # msg = input('Input your Task:')
            else:
                raise ValueError(f"illegal condition: {dec}")
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            save_error(e, error_trace, "declaration_error")
            break


def task_automation_vision(max_try=20):
    ui_id = 0
    for i in range(max_try):
        try:
            ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id,
                                                                       output_dir=pjoin(DATA_PATH, user_id, task_id))
            ui_data, action = uta.automate_task_vision(user_id=user_id, task_id=task_id, ui_img_file=ui_img,
                                                ui_xml_file=ui_xml, printlog=False)


            if action.get("Action") is not None and "error" in action["Action"].lower():
                save_error(action["Exception"], action["Traceback"], "automation_error")
                break

            annotate_screenshot = annotate_ui_operation(ui_data, action, show=False)
            screen_path = pjoin(DATA_PATH, user_id, task_id, f"{ui_id}_annotated.png")
            SystemConnector().save_img(annotate_screenshot, screen_path)
            # with open(screen_path, 'wb') as fp:
            #     fp.write(annotate_screenshot)

            if 'complete' in action['Action'].lower():
                break
            elif "user decision" in action['Action'].lower():
                input("Do the necessary operation and press Enter to continue...")
                ui_id += 1
                continue
            device.take_action(action=action, ui_data=ui_data, show=False)
            time.sleep(2)  # wait the action to be done
            ui_id += 1
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            save_error(e, error_trace, "automation_error")
            break


def task_automation(max_try=20):
    ui_id = 0
    for i in range(max_try):
        try:
            ui_img, ui_xml = device.cap_and_save_ui_screenshot_and_xml(ui_id=ui_id,
                                                                       output_dir=pjoin(DATA_PATH, user_id, task_id))
            package, activity = device.get_current_package_and_activity_name()
            keyboard_active = device.check_keyboard_active()
            ui_data, action = uta.automate_task(user_id=user_id, task_id=task_id, ui_img_file=ui_img,
                                                ui_xml_file=ui_xml,
                                                package_name=package, activity_name=activity,
                                                keyboard_active=keyboard_active, printlog=False)

            # ui_path = pjoin(DATA_PATH, user_id, task_id)
            # ui_tree = SystemConnector().load_json(pjoin(ui_path, f"{i}_uitree.json"))
            # ui_data = SystemConnector().load_ui_data(pjoin(ui_path, f"{i}.png"), pjoin(ui_path, f"{i}.xml"), resolution)
            # ui_data.elements = ui_tree

            if action.get("Action") is not None and "error" in action["Action"].lower():
                save_error(action["Exception"], action["Traceback"], "automation_error")
                break

            annotate_screenshot = annotate_ui_operation(ui_data, action)
            screen_path = pjoin(DATA_PATH, user_id, task_id, f"{ui_id}_annotated.png")
            SystemConnector().save_img(annotate_screenshot, screen_path)
            # with open(screen_path, 'wb') as fp:
            #     fp.write(annotate_screenshot)

            if 'complete' in action['Action'].lower():
                break
            elif "user decision" in action['Action'].lower():
                input("Do the necessary operation and press Enter to continue...")
                continue

            device.take_action(action=action, ui_data=ui_data, show=False)
            time.sleep(2)  # wait the action to be done
            ui_id += 1
        except Exception as e:
            print(e)
            error_trace = traceback.format_exc()  # Get the stack trace
            save_error(e, error_trace, "automation_error")
            break


def save_error(e, error_trace, save_name):
    error_json = {
        'error': str(e),
        'traceback': error_trace  # Save the stack trace in the JSON
    }
    task_folder = pjoin(DATA_PATH, user_id, task_id)
    if not os.path.exists(task_folder):
        os.makedirs(task_folder)
    error_path = pjoin(task_folder, f"{save_name}.json")
    SystemConnector().save_json(error_json, error_path)


# set up user task
user_id = 'user64'
# init device
device = Device()
device.connect()

resolution = device.get_device_resolution()
# init uta
uta = UTA()
uta.setup_user(user_id=user_id, device_resolution=resolution, app_list=app_list)

for task_idx, task in enumerate(task_list2):
    # if task_idx + 1 not in [16, 21, 25, 9, 31, 32, 37, 44, 45, 49, 55]:
    #     continue
    if task_idx + 1 not in [1, 12, 7, 14]:
        continue
    # if task_idx < 21:
    #     continue
    # if not 46 <= task_idx < 54:
    #     continue
    # if 'uber' in task.lower() or 'book' in task.lower() or 'whatsapp' in task.lower():
    #     continue
    # if task_info_list2[task_idx][1] != 'Feasible':
    #     continue
    task_id = f"task{task_idx + 1}"

    # task declaration
    task_declaration(task, max_try=10)

    # task automation
    device.go_homepage()
    user, task_obj = uta.instantiate_user_task(user_id, task_id)
    device.reboot_app(task_obj.involved_app_package)
    task_automation_vision(max_try=10)

    # direct run
    # device.go_homepage()
    # device.reboot_app(app_list2[task_idx])
    # uta.auto_task(task_desc=task, task_id=task_id, device=device, show_ui=False, printlog=False, wait_time=3)

# single test
# device.go_homepage()
# device.reboot_app("com.google.android.apps.maps")
# uta.auto_task(task_desc="search data61 in maps", task_id="100", device=device, show_ui=False, printlog=False, wait_time=3)

device.disconnect()
