import os
import ctypes
import time
from PIL import Image
from pystray import Icon, MenuItem as item
import win32con, win32api
import threading
from winotify import Notification

def notif(title,msg,write=True,cnt=None):
    Notification(app_id="椰羊自动化",title=title,msg=msg,icon=os.getcwd() + "\\imgs\\icon.png").show()
    if write:
        if os.path.exists('.notif'):
            with open('.notif','r') as fh:
                cnt=fh.readline().strip('\n')
        if cnt is None:
            cnt = '0'
        with open('.notif','w') as fh:
            fh.write(cnt+'\n'+title+'\n'+msg)

def show_notification(icon, item):
    ctypes.windll.user32.MessageBoxW(0, "程序已在运行！", "提示", 0x40)
    icon.stop()


def exit_program(icon, item):
    icon.stop()
    os._exit(0)

def maopao(icon, item):
    file_name = '.notif'
    cnt='0'
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            cnt=file.readline().strip('\n')
    with open(file_name, 'w') as file:
        file.write(f"{cnt}\n喵\nQwQ")
    win32api.SetFileAttributes(file_name, win32con.FILE_ATTRIBUTE_HIDDEN)

def notify():
    file_name = '.notif'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            file.write("0")
        win32api.SetFileAttributes(file_name, win32con.FILE_ATTRIBUTE_HIDDEN)
    last = os.path.getmtime(file_name)
    while 1:
        time.sleep(0.5)
        if last != os.path.getmtime(file_name):
            with open(file_name,'r') as fh:
                s=fh.readlines()
            if len(s)>=3:
                notif(s[1].strip('\n'),s[2].strip('\n'),0)
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
        item('冒泡', maopao),
        item('退出', exit_program),
    )
    icon.menu = menu

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
