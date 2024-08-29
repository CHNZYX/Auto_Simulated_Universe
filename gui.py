import atexit
import flet as ft
import pyuac
import threading
import os
import sys
import psutil
import shutil

from utils.gui.choose import choose_view
from utils.gui.config_simul import config_view as config_view_simul
from utils.gui.config_diver import config_view as config_view_diver
from utils.gui.abyss import abyss_view
from utils.gui.common import Page, init_page


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
    name = current_process.name()
    if name.endswith('.exe') and name != 'python.exe':
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

def clean_temp_files():
    try:
        path = sys._MEIPASS
    except:
        return
    now_dir = path
    parent_dir = os.path.dirname(now_dir)
    for file in os.listdir(parent_dir):
        file_path = os.path.join(parent_dir, file)
        if os.path.basename(now_dir) != file and os.path.isdir(file_path) and file.startswith('_MEI'):
            files_list = os.listdir(file_path)
            if 'utils' not in files_list or 'flet' not in files_list or 'win32' not in files_list:
                continue
            utils_path = os.path.join(file_path, 'utils')
            utils_list = os.listdir(utils_path)
            if 'models' not in utils_list:
                continue
            models_path = os.path.join(utils_path, 'models')
            models_list = os.listdir(models_path)
            if 'ppocr_keys_v1.txt' not in models_list or 'v3_det.onnx' not in models_list or 'v4_rec.onnx' not in models_list:
                continue
            try:
                shutil.rmtree(file_path, ignore_errors=True)
            except:
                pass

if __name__ == "__main__":
    atexit.register(cleanup)
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        threading.Thread(target=clean_temp_files).start()
        ft.app(target=main)
    cleanup()