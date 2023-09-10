import time
import os
import shutil
import pythoncom
import win32com.client,win32gui
pythoncom.CoInitialize()
shell = win32com.client.Dispatch("WScript.Shell")
shell.SendKeys(" ")  # Undocks my focus from Python IDLE
game_nd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
win32gui.SetForegroundWindow(game_nd)