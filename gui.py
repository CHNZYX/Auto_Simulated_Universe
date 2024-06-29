import atexit
import flet as ft
import pyuac
import win32gui
import os
import sys
import psutil

from utils.gui.choose import choose_view
from utils.gui.config_simul import config_view as config_view_simul
from utils.gui.config_diver import config_view as config_view_diver
from utils.gui.abyss import abyss_view
from utils.gui.common import mynd, Page, init_page


def main(page: Page):
    def on_route_change(e: Page):
        page.views.clear()
        choose_view(page)
        if e.route == "/config_simul":
            config_view_simul(page)
        if e.route == "/config_diver":
            config_view_diver(page)
        if e.route == '/abyss':
            abyss_view(page)
        page.update()

    def view_pop():
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


    init_page(page)
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.PINK,
    )
    page.title = "AutoSimulatedUniverse"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.on_route_change = on_route_change
    page.on_view_pop = view_pop
    page.window_min_width = 800
    page.window_width = 800
    page.window_height = 670
    page.window_min_height = 650
    page.go(page.route)

def cleanup():
    current_process = psutil.Process(os.getpid())
    if current_process.name().endswith('.exe'):
        try:
            father = current_process.parent()
            try:
                father.terminate()
            except:
                pass
            try:
                father.kill()
            except:
                pass
            psutil.wait_procs([father], timeout=5)
        except:
            pass
    os._exit(0)

if __name__ == "__main__":
    atexit.register(cleanup)
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        ft.app(target=main)
    cleanup()