import traceback
from typing import Optional

from flet_core import MainAxisAlignment, CrossAxisAlignment, Page, ControlEvent

import flet as ft
import pyuac

from align_angle import main as align_angle
from states import SimulatedUniverse, version
from utils.config import config

debug_mode = False
show_map_mode = False
su: Optional[SimulatedUniverse] = None


def show_snack_bar(page, text, color, selectable=False):
    return page.show_snack_bar(
        ft.SnackBar(
            open=True,
            content=ft.Text(text, selectable=selectable),
            bgcolor=color,
        )
    )


def choose_view(page: Page):
    def change_all_button(value: bool = True):
        for i in page.views[0].controls[0].controls:
            if isinstance(i, ft.FilledButton):
                i.disabled = value
        page.views[0].controls[0].controls[-1].disabled = False
        page.update()

    def run(func, *args, **kwargs):
        try:
            change_all_button()
            return func(*args, **kwargs)
        except Exception:
            print("E: 运行函数时出现错误")
            traceback.print_exc()
        finally:
            change_all_button(False)

    def angle(_e):
        show_snack_bar(page, "开始校准，请切换回游戏", ft.colors.GREEN)
        run(align_angle)

    def start(_e):
        global su
        show_snack_bar(page, "开始运行，请切换回游戏", ft.colors.GREEN)
        su = run(SimulatedUniverse, 1, int(debug_mode), int(show_map_mode))
        run(su.start)

    def start_new(_e):
        global su
        show_snack_bar(page, "开始录入，请切换回游戏", ft.colors.GREEN)
        su = run(SimulatedUniverse, 0, int(debug_mode), int(show_map_mode))
        run(su.start)

    def stop(_e):
        show_snack_bar(page, "尝试停止运行", ft.colors.GREEN)
        if su is not None:
            run(su.stop)

    def show_map_checkbox_changed(_e):
        global show_map_mode
        show_map_mode = not show_map_mode

    def debug_checkbox_changed(_e):
        global debug_mode
        debug_mode = not debug_mode

    def difficult_changed(e: ControlEvent):
        config.difficult = e.data
        config.save()

    def fate_changed(e: ControlEvent):
        config.fate = e.data
        config.save()

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
                            "停止",
                            icon=ft.icons.STOP,
                            on_click=stop,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Checkbox(
                            label="显示地图",
                            value=False,
                            on_change=show_map_checkbox_changed,
                        ),
                        ft.Checkbox(
                            label="调试模式",
                            value=False,
                            on_change=debug_checkbox_changed,
                        ),
                        ft.Dropdown(
                            width=100,
                            label="难度",
                            hint_text="选择世界难度",
                            options=[
                                ft.dropdown.Option("1"),
                                ft.dropdown.Option("2"),
                                ft.dropdown.Option("3"),
                                ft.dropdown.Option("4"),
                                ft.dropdown.Option("5"),
                            ],
                            value=config.difficult,
                            on_change=difficult_changed,
                        ),
                        ft.Dropdown(
                            width=100,
                            label="命途",
                            hint_text="选择命途",
                            options=[
                                ft.dropdown.Option("存护"),
                                ft.dropdown.Option("记忆"),
                                ft.dropdown.Option("虚无"),
                                ft.dropdown.Option("丰饶"),
                                ft.dropdown.Option("巡猎"),
                                ft.dropdown.Option("毁灭"),
                                ft.dropdown.Option("欢愉"),
                            ],
                            value=config.fate,
                            on_change=fate_changed,
                        )
                    ],
                ),
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            vertical_alignment=MainAxisAlignment.CENTER,
        )
    )


def main(page: Page):
    def on_route_change(_: Page):
        page.views.clear()
        choose_view(page)
        page.update()

    page.title = "AutoSimulatedUniverse"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.on_route_change = on_route_change
    page.window_min_width = 800
    page.window_width = 800
    page.window_height = 600
    page.window_min_height = 600
    page.go(page.route)


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        ft.app(target=main)
