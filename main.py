from testing.Device import Device
device = Device()
device.connect()

from uta.UTA import UTA
uta = UTA()

uta.auto_task(task_desc='search data61 in maps', task_id='1', device=device, show_ui=True, printlog=True, wait_time=3)