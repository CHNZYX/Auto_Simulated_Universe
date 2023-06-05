import os
import ctypes
import tkinter as tk
import time
from PIL import Image
from pystray import Icon, MenuItem as item
import win32gui
from gui.common import mynd
import threading
from utils.utils import notif


def hide_window():
    window = tk.Tk()
    window.withdraw()


def show_notification(icon, item):
    ctypes.windll.user32.MessageBoxW(0, "程序已在运行！", "提示", 0x40)
    icon.stop()


def exit_program(icon, item):
    icon.stop()
    os._exit(0)

def notify():
    file_name = '.notif'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            file.write(" ")
    last = os.path.getmtime(file_name)
    while 1:
        time.sleep(0.5)
        if last != os.path.getmtime(file_name):
            with open(file_name,'r') as fh:
                s=fh.readlines()
            if len(s)==2:
                notif(s[0].strip('\n'),s[1].strip('\n'),0)
            last = os.path.getmtime(file_name)

def main():
    # 检测程序是否已经在运行
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "YEYANG_MyProgramMutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        show_notification(None, None)
        return

    # 创建系统托盘图标
    image = Image.open("imgs/icon.png")
    icon = Icon("椰羊自动化", image, "椰羊自动化")
    menu = (
        item('退出', exit_program),
    )
    icon.menu = menu

    try:
        win32gui.ShowWindow(mynd, 0)
    except:
        pass

    t_notify = threading.Thread(target=notify)
    t_notify.start()
    # 显示系统托盘图标
    icon.run()


if __name__ == '__main__':
    main()
