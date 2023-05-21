import traceback
from typing import Optional

from flet_core import MainAxisAlignment, CrossAxisAlignment, Page

import flet as ft
import pyuac

from align_angle import main as align_angle
from states import SimulatedUniverse, version

debug_mode = False
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
        su = run(SimulatedUniverse, 1, int(debug_mode))
        run(su.start)

    def start_new(_e):
        global su
        show_snack_bar(page, "开始录入，请切换回游戏", ft.colors.GREEN)
        su = run(SimulatedUniverse, 0, int(debug_mode))
        run(su.start)

    def stop(_e):
        show_snack_bar(page, "尝试停止运行", ft.colors.GREEN)
        if su is not None:
            run(su.stop)

    def checkbox_changed(_e):
        global debug_mode
        debug_mode = not debug_mode

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
                            label="调试模式",
                            value=False,
                            on_change=checkbox_changed,
                        ),
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
