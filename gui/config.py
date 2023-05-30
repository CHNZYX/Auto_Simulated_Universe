from flet_core import MainAxisAlignment, ControlEvent, CrossAxisAlignment
import flet as ft

from gui.common import show_snack_bar, Page
from utils.config import config


def config_view(page: Page):
    def back_choose(_):
        page.go("/")
        page.update()

    def save(_):
        config.save()
        show_snack_bar(page, "保存成功", ft.colors.GREEN)

    def show_map_checkbox_changed(_e):
        page.show_map_mode = not page.show_map_mode

    def debug_checkbox_changed(_e):
        page.debug_mode = (page.debug_mode + 1) % 3

    def difficult_changed(e: ControlEvent):
        config.difficult = e.data

    def fate_changed(e: ControlEvent):
        config.fate = e.data

    def textbox_changed(e):
        config.order_text = e.control.value

    page.views.append(
        ft.View(
            "/config",
            [
                ft.Stack(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(
                                        value="设置",
                                        size=30,
                                    ),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "返回",
                                                icon=ft.icons.ARROW_BACK,
                                                on_click=back_choose,
                                            ),
                                            ft.ElevatedButton(
                                                "保存",
                                                icon=ft.icons.DONE,
                                                on_click=save,
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.CENTER,
                                        spacing=50,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=10,
                        ),
                    ]
                ),
                ft.Divider(
                    height=1,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Checkbox(
                                            label="显示地图",
                                            value=False,
                                            on_change=show_map_checkbox_changed,
                                        ),
                                        ft.Checkbox(
                                            label="调试模式",
                                            value=False,
                                            tristate=True,
                                            on_change=debug_checkbox_changed,
                                        ),
                                    ]
                                ),
                                ft.Row(
                                    [
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
                                        ),
                                    ]
                                ),
                                ft.TextField(
                                    label="配队",
                                    width=80,
                                    value=config.order_text,
                                    on_change=textbox_changed,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
            ],
            padding=0,
            spacing=0,
        )
    )
