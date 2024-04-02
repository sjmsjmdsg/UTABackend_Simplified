import cv2
import time
from testing import data_util
import glob
import tqdm

from uta.DataStructures import *
from uta.ModelManagement import ModelManager
from uta.ModelManagement.OpenAI import _OpenAI
from uta.ModelManagement.GoogleOCR import _GoogleOCR

from uta.SystemConnection import _Local, SystemConnector
from uta.UIProcessing import UIProcessor, _UIChecker
from uta.TaskDeclearation import TaskDeclarator
from testing.Device import Device

from uta.ThirdPartyAppManagement import ThirdPartyAppManager, _GooglePlay
from uta.TaskAction import _TaskUIChecker, TaskActionChecker
from uta.AvailableTaskList import TaskList

from uta.config import *
from uta import UTA

app_list = ['com.android.systemui.auto_generated_rro_vendor__', 'com.google.android.providers.media.module', 'com.google.android.overlay.permissioncontroller', 'com.google.android.overlay.googlewebview', 'com.android.calllogbackup', 'com.android.carrierconfig.auto_generated_rro_vendor__', 'com.android.systemui.accessibility.accessibilitymenu', 'com.android.internal.emulation.pixel_3_xl', 'com.android.providers.contacts', 'com.android.internal.emulation.pixel_4a', 'com.android.dreams.basic', 'com.android.companiondevicemanager', 'com.android.cts.priv.ctsshim', 'com.google.android.calendar', 'com.google.android.networkstack.tethering.emulator', 'com.google.android.contacts', 'com.android.mms.service', 'com.google.android.cellbroadcastreceiver', 'com.android.providers.downloads', 'com.android.bluetoothmidiservice', 'com.android.credentialmanager', 'com.google.android.printservice.recommendation', 'com.google.android.captiveportallogin', 'com.android.storagemanager.auto_generated_rro_product__', 'com.google.android.networkstack', 'com.google.android.overlay.googleconfig', 'com.android.keychain', 'com.google.android.tag', 'com.android.internal.emulation.pixel_2_xl', 'android.auto_generated_rro_vendor__', 'com.google.android.apps.wellbeing', 'com.android.nfc.auto_generated_rro_product__', 'com.android.virtualmachine.res', 'com.android.emulator.multidisplay', 'com.android.shell', 'com.google.android.adservices.api', 'com.google.android.wifi.dialog', 'com.google.android.apps.wallpaper.nexus', 'com.android.inputdevices', 'com.google.android.ondevicepersonalization.services', 'com.google.android.apps.customization.pixel', 'com.android.bookmarkprovider', 'com.google.android.onetimeinitializer', 'com.google.android.permissioncontroller', 'com.google.android.overlay.largescreenconfig', 'com.android.internal.emulation.pixel_6a', 'com.android.sharedstoragebackup', 'com.android.imsserviceentitlement', 'com.android.providers.media', 'com.android.providers.calendar', 'com.android.providers.blockednumber', 'com.google.android.documentsui', 'com.google.android.googlesdksetup', 'com.android.carrierconfig.auto_generated_rro_product__', 'com.google.android.devicelockcontroller', 'com.android.proxyhandler', 'com.android.systemui.emulation.pixel_3a', 'com.android.emergency.auto_generated_rro_product__', 'com.android.managedprovisioning', 'com.android.emergency', 'com.google.android.telephony.satellite', 'com.android.managedprovisioning.auto_generated_rro_product__', 'com.google.android.gm', 'com.android.carrierdefaultapp', 'com.android.backupconfirm', 'com.google.android.hotspot2.osulogin', 'com.android.nfc', 'com.google.android.deskclock', 'com.android.mtp', 'com.android.systemui.emulation.pixel_4a', 'com.google.android.gsf', 'com.google.android.overlay.pixelconfigcommon', 'com.android.internal.display.cutout.emulation.double', 'com.android.theme.font.notoserifsource', 'com.android.traceur.auto_generated_rro_product__', 'com.google.android.health.connect.backuprestore', 'com.google.android.settings.intelligence', 'com.android.systemui.emulation.pixel_3', 'com.android.systemui', 'com.android.wallpapercropper', 'com.android.internal.emulation.pixel_4', 'com.android.systemui.emulation.pixel_7', 'com.android.internal.emulation.pixel_fold', 'com.android.internal.emulation.pixel_5', 'com.android.systemui.emulation.pixel_6', 'com.android.providers.contacts.auto_generated_rro_product__', 'com.google.android.dialer', 'com.android.systemui.emulation.pixel_5', 'com.android.internal.emulation.pixel_3', 'com.android.systemui.emulation.pixel_4', 'com.android.internal.emulation.pixel_6', 'com.android.internal.systemui.navbar.gestural', 'com.android.internal.emulation.pixel_7', 'com.android.role.notes.enabled', 'com.google.android.apps.nexuslauncher', 'com.google.mainline.adservices', 'com.google.android.apps.wallpaper', 'com.android.internal.emulation.pixel_6_pro', 'com.google.android.federatedcompute', 'com.google.android.webview', 'com.google.android.sdksandbox', 'com.android.internal.emulation.pixel_3a', 'com.android.wallpaperbackup', 'com.android.systemui.emulation.pixel_6a', 'com.google.android.cellbroadcastservice', 'com.android.internal.systemui.navbar.twobutton', 'com.android.internal.systemui.navbar.threebutton', 'com.android.egg', 'com.android.systemui.emulation.pixel_fold', 'com.android.localtransport', 'android', 'com.android.camera2', 'com.android.systemui.emulation.pixel_3a_xl', 'com.android.providers.settings.auto_generated_rro_product__', 'com.google.android.soundpicker', 'com.google.android.packageinstaller', 'com.android.se', 'com.android.pacprocessor', 'com.google.android.connectivity.resources.goldfish.overlay', 'com.google.android.safetycenter.resources', 'com.google.android.apps.youtube.music', 'com.android.stk', 'com.android.internal.display.cutout.emulation.hole', 'com.android.settings', 'com.android.bips', 'com.google.android.partnersetup', 'com.android.internal.systemui.navbar.gestural_narrow_back', 'com.android.internal.display.cutout.emulation.tall', 'com.google.android.networkstack.tethering', 'com.android.systemui.emulation.pixel_7_pro', 'com.google.android.projection.gearhead', 'com.android.cameraextensions', 'com.google.android.odad', 'com.android.carrierconfig', 'com.android.internal.systemui.navbar.gestural_wide_back', 'com.google.android.ext.shared', 'com.google.android.feedback', 'com.android.chrome', 'com.google.android.apps.maps', 'com.google.android.as', 'android.auto_generated_rro_product__', 'com.android.musicfx', 'com.android.internal.systemui.navbar.transparent', 'com.android.server.telecom.auto_generated_rro_product__', 'com.google.android.inputmethod.latin', 'com.android.providers.settings.auto_generated_rro_vendor__', 'com.google.android.systemui.gxoverlay', 'com.google.android.uwb.resources', 'com.android.providers.downloads.ui', 'com.google.android.wifi.resources', 'com.android.ons', 'com.google.android.healthconnect.controller', 'com.android.intentresolver', 'com.google.android.apps.docs', 'com.google.android.nearby.halfsheet', 'com.android.phone.auto_generated_rro_vendor__', 'com.android.certinstaller', 'com.google.android.apps.restore', 'com.android.internal.emulation.pixel_7_pro', 'com.android.simappdialog', 'com.android.providers.telephony', 'com.android.wallpaper.livepicker', 'com.android.internal.display.cutout.emulation.emu01', 'com.android.internal.display.cutout.emulation.waterfall', 'com.android.settings.auto_generated_rro_product__', 'com.google.android.rkpdapp', 'com.android.providers.settings', 'com.android.systemui.emulation.pixel_3_xl', 'com.android.phone', 'com.android.internal.systemui.navbar.gestural_extra_wide_back', 'com.android.internal.emulation.pixel_4_xl', 'com.android.traceur', 'com.google.android.as.oss', 'com.google.android.apps.messaging', 'com.android.systemui.emulation.pixel_6_pro', 'com.android.internal.emulation.pixel_3a_xl', 'com.android.location.fused', 'com.android.vpndialogs', 'com.android.cellbroadcastreceiver', 'com.android.systemui.plugin.globalactions.wallet', 'com.google.android.tts', 'com.android.systemui.emulation.pixel_4_xl', 'com.google.android.googlequicksearchbox', 'com.google.android.modulemetadata', 'com.android.phone.auto_generated_rro_product__', 'com.android.systemui.accessibility.accessibilitymenu.auto_generated_rro_product__', 'com.android.htmlviewer', 'com.android.vending', 'com.google.android.ext.services', 'com.google.android.overlay.largescreensettingsprovider', 'com.google.android.configupdater', 'com.google.android.gms.supervision', 'com.android.providers.userdictionary', 'com.android.cts.ctsshim', 'com.google.android.apps.photos', 'com.android.bluetooth', 'com.google.android.markup', 'com.android.emulator.radio.config', 'com.android.internal.display.cutout.emulation.corner', 'com.google.android.gms', 'com.android.storagemanager', 'com.android.printspooler', 'com.android.systemui.auto_generated_rro_product__', 'com.android.providers.partnerbookmarks', 'com.android.soundpicker', 'com.google.mainline.telemetry', 'com.android.dynsystem', 'com.google.android.bluetooth', 'com.android.providers.telephony.auto_generated_rro_product__', 'com.google.android.connectivity.resources', 'com.android.bips.auto_generated_rro_product__', 'com.google.android.youtube', 'com.android.simappdialog.auto_generated_rro_product__', 'com.android.externalstorage', 'com.android.server.telecom']


def test_task():
    task = Task("1", "1", "Open Youtube")
    print(task)
    print(task.to_dict())

    new_task = {'task_id': "2", "user_id": "2", "task_description": "Close Youtube", "fake_attr": "abc"}
    task.load_from_dict(new_task)
    print(task.to_dict())

    action = {"Action": "Long Press", "Element Id": "19", "Description": "N/A", "Input Text": "N/A", "Reason": "N/A"}
    task.actions.append(action)
    print(task.to_dict())


def test_llmmodel():
    llm_model = _OpenAI()
    conversation = []
    while True:
        user_input = input()
        user_input = {'role': 'user', 'content': user_input}
        conversation.append(user_input)
        msg = llm_model.send_openai_conversation(conversation, printlog=True, runtime=True)
        print(msg)
        conversation.append(msg)


def test_googleocr():
    img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    google_ocr = _GoogleOCR()
    img_data2 = google_ocr.detect_text_ocr(img_path, output_dir=WORK_PATH + 'old_test_data/test/output/',
                                           show=True, shrink_size=True)
    print(img_data2)


def test_iconclassifier():
    img_path = WORK_PATH + 'old_test_data/test/classification/a1.jpg'
    icon_classifier = _IconClassifier()
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = icon_classifier.classify_icons([img_rgb])
    print("Classification Result:", result)


def test_model_manager():
    model_manager = ModelManager()
    # conversation = []
    # for i in range(2):
    #     user_input = input()
    #     user_input = {'role': 'user', 'content': user_input}
    #     conversation.append(user_input)
    #     msg = model_manager.send_fm_conversation(conversation, printlog=True, runtime=True)
    #     print(msg)
    #     conversation.append(msg)

    # img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    # img_data2 = model_manager.detect_text_ocr(img_path)
    # print(img_data2)

    # img_path = WORK_PATH + 'old_test_data/test/classification/a1.jpg'
    # img = cv2.imread(img_path)
    # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # result = model_manager.classify_icons([img_rgb])
    # print("Classification Result:", result)

    token_counts = model_manager.count_token_size("I like apple.")
    print(token_counts)


def test_local():
    img_path = WORK_PATH + 'old_test_data/test/general/0.png'
    xml_path = WORK_PATH + 'old_test_data/test/general/0.xml'
    json_path = WORK_PATH + 'old_test_data/1/I want to see a youtube introducing canberra raiders, ' \
                                    'if there is any advertisement in the ' \
                                    'middle of playing, and it is skipable,please help me skip it/device/1.json'

    img_write_path = WORK_PATH + 'old_test_data/test/local/0.png'
    xml_write_path = WORK_PATH + 'old_test_data/test/local/0.xml'
    json_write_path = WORK_PATH + 'old_test_data/test/local/1.json'

    img = _Local().load_img(img_path)
    xml_file = _Local().load_xml(xml_path)
    json_file = _Local().load_json(json_path)

    print(img)
    print(xml_file)
    print(json_file)

    _Local().save_img(img, img_write_path)
    _Local().save_xml(xml_file, xml_write_path)
    _Local().save_json(json_file, json_write_path)
    print(1)


def test_systemcomnnector():
    system_connector = SystemConnector()
    user = system_connector.load_user("user1")
    task = system_connector.load_task("user1", "task1")

    screenshot = DATA_PATH + 'user1/task1/0.png'
    xml_file = DATA_PATH + 'user1/task1/0.xml'
    ui_data = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file)

    print(user.to_dict())
    print(task.to_dict())
    print(ui_data.to_dict())

    system_connector.save_task(task)
    system_connector.save_user(user)
    system_connector.save_ui_data(ui_data, DATA_PATH + 'user1/task1/')


def test_uiprocessor():
    model_manager = ModelManager()
    ui_processor = UIProcessor(model_manager)

    screenshot = DATA_PATH + 'user1/task6/4.png'
    xml_file = DATA_PATH + 'user1/task6/4.xml'
    ui_data = UIData(screenshot_file=screenshot, xml_file=xml_file, resolution=(1080, 2400))
    print(ui_data.to_dict())

    new_ui = ui_processor.process_ui(ui_data=ui_data, show=True)
    # new_ui.annotate_ui_operation({"Action": "Click", "Coordinate": 3, "Element Id": "3", "others": "N/A"})
    print(new_ui.to_dict())

    # board = new_ui.annotated_screenshot
    # cv2.imshow('long_press', cv2.resize(board, (board.shape[1] // 3, board.shape[0] // 3)))
    # cv2.waitKey()
    # cv2.destroyWindow('long_press')


def test_task_declarator():
    model_manager = ModelManager()
    task_declarator = TaskDeclarator(model_manager)
    # description = "I want to watch football videos"
    description = "How are you today?"
    task = Task("1", "1", description)
    print(task.to_dict())

    resp = task_declarator.clarify_task(task, app_list=app_list, printlog=True)
    print(resp)
    print(task.to_dict())

    user_input = input()
    task.clarification_user_msg = user_input

    resp = task_declarator.justify_user_message(task, printlog=True)
    print(resp)
    print(task.to_dict())

    resp = task_declarator.clarify_task(task, app_list=app_list, printlog=True)
    print(resp)
    print(task.to_dict())
    #
    # user_input = input()
    # task.clarification_user_msg = user_input

    # resp = task_declarator.clarify_task(task, app_list=app_list, printlog=True)
    # print(resp)
    # print(task.to_dict())
    # resp = task_declarator.classify_task(task)
    # print(resp)
    # print(task.to_dict())
    # resp = task_declarator.decompose_task(task)
    # print(resp)
    # print(task.to_dict())


def test_googleplay():
    google_play = _GooglePlay()
    print(google_play.search_app_by_name('youtube'))
    print(google_play.search_apps_fuzzy('youtube'))


def test_appmanager():
    model_manager = ModelManager()
    app_manager = ThirdPartyAppManager(model_manager)

    app_list = ['com.google.android.apps.youtube YouTube',
                'com.google.android.apps.youtube.kids YouTube Kids',
                'com.google.android.apps.youtube.unplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.music YouTube Music',
                'com.google.android.youtube.tv YouTube for Android TV',
                'com.google.android.youtube.tvunplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.creator YouTube Studio',
                'com.google.android.apps.youtube.music.pwa YouTube Music for Chromebook',
                'com.google.android.youtube.tvkids YouTube Kids for Android TV',
                'com.google.android.youtube.tvmusic YouTube Music',
                'com.google.android.videos Google TV',
                'com.netflix.mediaclient Netflix',
                'com.tubitv Tubi: Movies & Live TV',
                'com.amazon.avod.thirdpartyclient Amazon Prime Video',
                'com.google.android.apps.youtube.producer YouTube Create',
                'com.disney.disneyplus Disney+',
                'com.vimeo.android.videoapp Vimeo',
                'com.crunchyroll.crunchyroid Crunchyroll',
                'com.hulu.plus Hulu: Stream TV shows & movies',
                'com.plexapp.android Plex: Stream Movies & TV']
    task = Task("1", "1", "I want to watch a football match with my mobile.")
    res = app_manager.check_related_apps(task, app_list, printlog=True)
    print(res)


def test_device():
    device = Device()
    # print(device.is_connected())
    # device.connect()
    # print(device.is_connected())
    # device.disconnect()
    # print(device.is_connected())
    device.connect()

    wm = device.get_device_resolution()
    print(wm)

    print(device.get_app_list_on_the_device())
    # device.launch_app('com.android.settings')
    # print(device.get_current_package_and_activity_name())
    # print(device.get_device())
    # print(device.get_device_name())
    # print(device.check_keyboard_active())
    # device.go_back()
    # device.close_app('com.google.android.youtube')

    # img_write_path = WORK_PATH + 'old_test_data/test/guidata/1.png'
    # screen = device.cap_screenshot()
    # _Local().save_img(screen, img_write_path)
    # print(device.cap_current_ui_hierarchy_xml())
    # screen_path, xml_path = device.cap_and_save_ui_screenshot_and_xml("2", WORK_PATH + 'old_test_data/test/guidata/')
    # print(screen_path, xml_path)

    # elements = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_elements.json')
    # tree = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_tree.json')
    # system_connector = SystemConnector()
    # screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    # xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    # gui = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file)
    # gui.elements = elements
    # gui.element_tree = tree

    # device.right_swipe_screen(gui, 0, True)
    # device.left_swipe_screen(gui, 0, True)
    # device.up_scroll_screen(gui, 0, True)
    # device.down_scroll_screen(gui, 0, True)
    # device.long_press_screen(gui, 19, True)
    # device.click_screen(gui, 19, True)

    # for act in ["Swipe", "Scroll", "Click", "Launch"]:
    #     cood = 0 if act != "Click" else 19
    #     cood_ele = gui.elements[cood]
    #     action = {"Action": act, "Coordinate": cood_ele, "Element Id": str(cood), "App": 'com.google.android.youtube',
    #               "Input Text": "something."}
    #     device.take_action(action, ui_data=gui, show=False)
    #     time.sleep(3)

    # test input independently
    # cood = 19
    # cood_ele = gui.elements[cood]
    # act = "Input"
    # action = {"Action": act, "Coordinate": cood_ele, "Element Id": str(cood), "App": 'com.google.android.youtube',
    #           "Input Text": "something."}
    # device.take_action(action, ui_data=gui, show=True)


def test_taskuichecker():
    model_manager = ModelManager()
    task_ui_checker = _TaskUIChecker(model_manager)

    elements = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_elements.json')
    tree = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_tree.json')
    system_connector = SystemConnector()
    screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    wm = (1080, 2400)
    gui = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file, ui_resize=wm)
    gui.elements = elements
    gui.element_tree = tree

    task = Task("1", "1", 'Open the youtube')
    new_prompt = task_ui_checker.wrap_task_context(task)
    print(1, new_prompt)
    new_prompt += task_ui_checker.wrap_task_info_after(task)
    print(2, new_prompt)

    # res = {'content': '{"Action": "Click", "Element Id": "3", "Reason": "Open Settings to access task settings"}'}
    # res = task_ui_checker.transfer_to_dict(res)
    # print(res)
    # res = {'content': '{"Action": "Click", "Element Id": "3", "Reason": "Open Settings to access task settings"}}\n'}
    # res = task_ui_checker.transfer_to_dict(res)
    # print(res)

    task.involved_app_package = "com.google.android.youtube"
    res = task_ui_checker.check_ui_relation(gui, task, printlog=True)
    print(task.to_dict())
    print(res)

    res = task_ui_checker.check_element_action(gui, task, printlog=True)
    print(task.to_dict())
    print(res)
    task.actions.append(res)

    res = task_ui_checker.check_element_action(gui, task, printlog=True)
    print(task.to_dict())
    print(res)

    res = task_ui_checker.check_ui_go_back_availability(gui, task, printlog=True)
    print(task.to_dict())
    print(res)

    task = Task("1", "1", 'Open the CSIRO app')
    task.involved_app_package = "com.google.csiro"
    res = task_ui_checker.check_ui_relation(gui, task, printlog=True)
    print(task.to_dict())
    print(res)




def test_actionchecker():
    model_manager = ModelManager()
    task_action_checker = TaskActionChecker(model_manager)

    task = Task("1", "1", 'How is the weather like today?')
    res = task_action_checker.action_inquiry(task, printlog=True)
    print(res)
    print(task.to_dict())

    elements = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_elements.json')
    tree = _Local().load_json(WORK_PATH + 'old_test_data/test/guidata/0_tree.json')
    system_connector = SystemConnector()
    screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    wm = (1080, 2400)
    gui = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file, ui_resize=wm)
    gui.elements = elements
    gui.element_tree = tree

    for sub_task in ['Go to the phone camera', 'Go to the Youtube', 'Go to the CSIRO app', 'Go to the home page']:
        task = Task("1", "1", sub_task)
        task.involved_app_package = "com.google.android.youtube"
        res = task_action_checker.action_on_ui(gui, task, printlog=True)
        print(res)
        print(task.to_dict())


def get_package():
    device = Device()
    device.connect()

    print(device.get_current_package_and_activity_name())
    print(device.get_app_list_on_the_device())


def test_uta():
    uta = UTA()
    user_id = "3"
    resolution = (1080, 2400)
    app_list = ['com.google.android.apps.youtube YouTube',
                'com.google.android.apps.youtube.kids YouTube Kids',
                'com.google.android.apps.youtube.unplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.music YouTube Music',
                'com.google.android.youtube.tv YouTube for Android TV',
                'com.google.android.youtube.tvunplugged YouTube TV: Live TV & more',
                'com.google.android.apps.youtube.creator YouTube Studio',
                'com.google.android.apps.youtube.music.pwa YouTube Music for Chromebook',
                'com.google.android.youtube.tvkids YouTube Kids for Android TV',
                'com.google.android.youtube.tvmusic YouTube Music',
                'com.google.android.videos Google TV',
                'com.netflix.mediaclient Netflix',
                'com.tubitv Tubi: Movies & Live TV',
                'com.amazon.avod.thirdpartyclient Amazon Prime Video',
                'com.google.android.apps.youtube.producer YouTube Create',
                'com.disney.disneyplus Disney+',
                'com.vimeo.android.videoapp Vimeo',
                'com.crunchyroll.crunchyroid Crunchyroll',
                'com.hulu.plus Hulu: Stream TV shows & movies',
                'com.plexapp.android Plex: Stream Movies & TV']
    uta.system_connector.user_data_root = WORK_PATH + 'old_test_data/test/user_info/'

    uta.setup_user(user_id, resolution, app_list)
    uta.instantiate_user_task(user_id, "0", user_msg="Open the app")
    uta.instantiate_user_task(user_id, "0", user_msg="Open the app")
    uta.declare_task(user_id, "0", "Open the Youtube app")

    screenshot = WORK_PATH + 'old_test_data/test/guidata/0.png'
    xml_file = WORK_PATH + 'old_test_data/test/guidata/0.xml'
    package_name = "com.google.android.apps.nexuslauncher"
    activity_name = "com.google.android.apps.nexuslauncher.NexusLauncherActivity"
    ui, action = uta.automate_task(user_id, "0", screenshot, xml_file, package_name, activity_name, printlog=True)
    print(ui)
    print(action)


def test_app_list():
    device = Device()
    device.connect()
    local = _Local()
    app_list = device.get_app_list_on_the_device()
    for _idx, one_app in enumerate(app_list):
        print(_idx)
        device.go_homepage()
        device.launch_app(one_app)
        screenshot = device.cap_screenshot()
        local.save_img(screenshot, WORK_PATH + f'old_test_data/test/app_list_api31/{_idx}_{one_app}.png')
        print(1)
    device.disconnect()


def test_tasklist():
    model_manager = ModelManager()
    tasklist = TaskList(model_manager)

    task = Task("1", "1", "Open the camera.")

    res = tasklist.match_task_to_list(task)
    print(res)

    task.involved_app = "Android Camera"
    res = tasklist.match_app_to_applist(task, app_list)
    print(res)

    task = Task("1", "1", "Create a pin for the device")
    res = tasklist.match_task_to_list(task)
    print(res)


def test_uichecker():
    system_connector = SystemConnector()
    model_manager = ModelManager()
    ui_checker = _UIChecker(model_manager)

    screenshot = DATA_PATH + 'user1/task1/0.png'
    xml_file = DATA_PATH + 'user1/task1/0.xml'
    ui_data = system_connector.load_ui_data(screenshot_file=screenshot, xml_file=xml_file)

    res = ui_checker.check_ui_decision_page(ui_data)
    print(res)


def test_gpt4v():
    fm = _OpenAI()
    json_write_path = WORK_PATH + 'old_test_data/test/gpt-v/result31.json'

    root_dir = DATA_PATH + '/user31'
    saved_file = {}
    for one_dir in tqdm.tqdm(glob.glob(root_dir + '/task*')):
        saved_file[one_dir.split('\\')[-1]] = {}
        task = _Local().load_json(one_dir + '/task.json')
        task_desc = task['task_description']
        prompt = data_util.gpt4v_prompt.format(task=task_desc)
        for one_ui in glob.glob(one_dir + '/*.png'):
            if 'annotated' in one_ui:
                continue
            result = fm.send_gpt4_vision_img_paths(prompt=prompt, img_paths=[one_ui])
            saved_file[one_dir.split('\\')[-1]][one_ui.split('\\')[-1]] = result

        _Local().save_json(saved_file, json_write_path)


if __name__ == '__main__':
    # test_task()

    # test_llmmodel()
    # test_googleocr()
    # test_iconclassifier()
    # test_model_manager()

    # test_local()
    # test_systemcomnnector()
    # test_uiprocessor()
    # test_task_declarator()

    # test_googleplay()
    # test_appmanager()

    test_device()
    # get_package()
    # test_taskuichecker()
    # test_actionchecker()
    # test_uta()

    # test_app_list()
    # test_tasklist()
    # test_uichecker()

    # test_gpt4v()