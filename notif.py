import os
import ctypes
import tkinter as tk
import time
from PIL import Image
from pystray import Icon, MenuItem as item


def hide_window():
    window = tk.Tk()
    window.withdraw()


def show_notification(icon, item):
    ctypes.windll.user32.MessageBoxW(0, "程序已在运行！", "提示", 0x40)
    icon.stop()


def exit_program(icon, item):
    icon.stop()
    os._exit(0)


def main():
    # 检测程序是否已经在运行
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "YEYANG_MyProgramMutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        show_notification(None, None)
        return

    # 创建系统托盘图标
    image = Image.open("imgs/icon.jpg")
    icon = Icon("椰羊自动化", image, "椰羊自动化")
    menu = (
        item('退出', exit_program),
    )
    icon.menu = menu

    # 隐藏窗口
    # hide_window()

    # 显示系统托盘图标
    icon.run()
    while 1:
        print(233)
        time.sleep(1)


if __name__ == '__main__':
    main()
