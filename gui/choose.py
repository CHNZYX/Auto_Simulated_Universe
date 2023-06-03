import traceback

import flet as ft
import win32gui
from flet_core import MainAxisAlignment, CrossAxisAlignment

from align_angle import main as align_angle
from gui.common import show_snack_bar, mynd, Page
from states import SimulatedUniverse, version
from utils.config import config
from utils.update_map import update_map


def choose_view(page: Page):
    def change_all_button(value: bool = True):
        cnt = 0
        for i in page.views[0].controls[0].controls:
            if isinstance(i, ft.FilledButton):
                if cnt <= 2:
                    i.disabled = value
                    cnt += 1
                else:
                    i.disabled = False
        page.update()

    def run(func, *args, **kwargs):
        try:
            change_all_button()
            res=func(*args, **kwargs)
            change_all_button(False)
            return res
        except Exception:
            print("E: 运行函数时出现错误")
            traceback.print_exc()
        finally:
            change_all_button(False)

    def angle(_e):
        show_snack_bar(page, "开始校准，请切换回游戏（¬､¬）", ft.colors.GREEN)
        res = run(align_angle)
        if res == 1:
            show_snack_bar(page, "校准成功（＾∀＾●）", ft.colors.GREEN)
        else:
            show_snack_bar(page, "校准失败（⊙.⊙）", ft.colors.RED)

    def start(_e):
        if config.angle == "1.0":
            show_snack_bar(page, "没有校准,不准运行（￣^￣）", ft.colors.RED)
            return
        show_snack_bar(page, "开始运行，请切换回游戏（＾∀＾●）", ft.colors.GREEN)
        page.su = run(
            SimulatedUniverse, 1, int(config.debug_mode), int(config.show_map_mode)
        )
        run(page.su.start)

    def start_new(_e):
        show_snack_bar(page, "开始录入，请切换回游戏（≖‿≖✧）", ft.colors.GREEN)
        page.su = run(
            SimulatedUniverse, 0, int(config.debug_mode), int(config.show_map_mode)
        )
        run(page.su.start)

    def stops(_e):
        show_snack_bar(page, "停止运行（>∀<）", ft.colors.GREEN)
        if page.su is not None:
            run(page.su.stop)

    def hide(_e):
        try:
            if win32gui.IsWindowVisible(mynd):
                show_snack_bar(page, "隐藏命令行窗口", ft.colors.GREEN)
                win32gui.ShowWindow(mynd, 0)  # 隐藏命令行窗口
            else:
                show_snack_bar(page, "显示命令行窗口", ft.colors.GREEN)
                win32gui.ShowWindow(mynd, 1)  # 显示命令行窗口
        except:
            pass

    def update_maps(_e):
        show_snack_bar(page, "开始更新地图（´・н・‘）", ft.colors.GREEN)
        msg, col = update_map(config.force_update)
        show_snack_bar(page, msg, col)

    def go_config(_e):
        page.go("/config")

    # View
    page.views.append(
        ft.View(
            "/",
            [
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                "AutoSimulatedUniverse",
                                size=50,
                            ),
                        ),
                        ft.Container(
                            content=ft.Text(
                                version,
                                size=20,
                            ),
                        ),
                        ft.FilledButton(
                            "校准",
                            icon=ft.icons.ADD_TASK,
                            on_click=angle,
                        ),
                        ft.FilledButton(
                            "运行",
                            icon=ft.icons.LOGIN,
                            on_click=start,
                        ),
                        ft.FilledButton(
                            "录入",
                            icon=ft.icons.ADD,
                            on_click=start_new,
                        ),
                        ft.FilledButton(
                            "显隐",
                            icon=ft.icons.HIDE_SOURCE,
                            on_click=hide,
                        ),
                        ft.FilledButton(
                            "停止",
                            icon=ft.icons.STOP,
                            on_click=stops,
                        ),
                        ft.FilledButton(
                            "设置",
                            icon=ft.icons.SETTINGS,
                            on_click=go_config,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.BROWSER_UPDATED,
                            tooltip="更新地图",
                            icon_size=30,
                            on_click=update_maps,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.END,
                ),
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            vertical_alignment=MainAxisAlignment.CENTER,
        )
    )
