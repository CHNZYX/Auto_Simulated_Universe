import os
import ctypes
import time
from PIL import Image
from pystray import Icon, MenuItem as item
import threading
import sys
import os
from winotify import Notification
import psutil

def notif(title,msg):
    Notification(app_id="椰羊自动化",title=title,msg=msg,icon=os.getcwd() + "\\imgs\\icon.png").show()

def exit_program(icon, item):
    icon.stop()
    os._exit(0)

def maopao(icon=None, item=None):
    file_name = 'logs/notif.txt'
    cnt='0'
    tm=None
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding="utf-8",errors='ignore') as file:
            s=file.readlines()
            cnt=s[0].strip('\n')
            try:
                tm=s[3].strip('\n')
            except:
                pass
    if tm is None:
        tm = str(time.time())
    os.makedirs('logs',exist_ok=1)
    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(f"{cnt}\n喵\n计数:{cnt}\n{tm}")


def clear(icon=None, item=None):
    file_name = 'logs/notif.txt'
    tm = time.time()
    if os.path.exists(file_name):
        with open(file_name, 'w', encoding="utf-8",errors='ignore') as file:
            file.write('0\n清零\n计数:0\n{tm}')
            
def notify():
    file_name = 'logs/notif.txt'
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding="utf-8") as file:
            file.write("0")
    last = os.path.getmtime(file_name)
    while 1:
        time.sleep(0.5)
        if last != os.path.getmtime(file_name):
            with open(file_name,'r', encoding="utf-8",errors='ignore') as fh:
                s=fh.readlines()
            if len(s)>=3:
                notif(s[1].strip('\n'),s[2].strip('\n'))
            last = os.path.getmtime(file_name)

def main():
    # 检测程序是否已经在运行
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "YEYANG_MyProgramMutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(0, "程序已在运行！", "提示", 0x40)
        return

    # 创建系统托盘图标
    image = Image.open("imgs/icon.png")
    icon = Icon("椰羊自动化", image, "椰羊自动化")
    menu = (
        item('冒泡', maopao),
        item('清零', clear),
        item('退出', exit_program),
    )
    icon.menu = menu
    maopao()

    '''
    try:
        mynd = list_handles(f=lambda n:"notif" in n[-9:])[0]
        win32gui.ShowWindow(mynd, 0)
    except:
        pass
    '''

    t_notify = threading.Thread(target=notify)
    t_notify.start()
    # 显示系统托盘图标
    icon.run()


if __name__ == '__main__':
    main()