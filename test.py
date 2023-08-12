import os
import threading
import time
threading.Thread(target=os.system,kwargs={'command':'notif.exe'}).start()
time.sleep(2)
threading.Thread(target=os.system,kwargs={'command':'python notif.py'}).start()