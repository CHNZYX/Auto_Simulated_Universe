from typing import Optional

import flet as ft
import win32gui

from states import SimulatedUniverse


class Page(ft.Page):
    su: Optional[SimulatedUniverse]
    first: int
    bonus: bool


def init_page(page: Page):
    page.su = None
    page.first = 1
    page.bonus = False


def show_snack_bar(page, text, color, selectable=False):
    return page.show_snack_bar(
        ft.SnackBar(
            open=True,
            content=ft.Text(text, selectable=selectable),
            bgcolor=color,
        )
    )


def cleanup():
    try:
        win32gui.ShowWindow(mynd, 1)
    except:
        pass


def enum_windows_callback(hwnd, hwnds):
    class_name = win32gui.GetClassName(hwnd)
    name = win32gui.GetWindowText(hwnd)
    try:
        if (
            class_name == "ConsoleWindowClass"
            and win32gui.IsWindowVisible(hwnd)
            and "gui" in name[-7:]
        ):
            hwnds.append(hwnd)
    except:
        pass
    return True


def list_handles():
    hwnds = []
    win32gui.EnumWindows(enum_windows_callback, hwnds)
    hwnds.append(0)
    return hwnds


mynd = list_handles()[0]
