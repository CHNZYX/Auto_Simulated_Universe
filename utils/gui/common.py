from typing import Optional, Union

import flet as ft
import win32gui

from simul import SimulatedUniverse
from diver import DivergentUniverse
from abyss import Abyss


class Page(ft.Page):
    su: Optional[Union[SimulatedUniverse, DivergentUniverse]]
    ab: Optional[Abyss]
    first: int
    bonus: bool


def init_page(page: Page):
    page.su = None
    page.ab = None
    page.first = 1


def show_snack_bar(page, text, color, selectable=False):
    return page.show_snack_bar(
        ft.SnackBar(
            open=True,
            content=ft.Text(text, selectable=selectable),
            bgcolor=color,
        )
    )


def cleanup():
    pass


def enum_windows_callback(hwnd, hwnds, name):
    class_name = win32gui.GetClassName(hwnd)
    window_name = win32gui.GetWindowText(hwnd)
    try:
        if (
            name == window_name
        ):
            hwnds.append(hwnd)
    except:
        pass
    return True


def list_handles(name='AutoSimulatedUniverse'):
    hwnds = []
    win32gui.EnumWindows(lambda a,b:enum_windows_callback(a,b,name=name), hwnds)
    hwnds.append(0)
    return hwnds[0]
