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
        page.go("/")
        page.update()

    def show_map_checkbox_changed(_e):
        config.show_map_mode = (config.show_map_mode + 1) % 2

    def debug_checkbox_changed(_e):
        config.debug_mode = not config.debug_mode

    def speed_checkbox_changed(_e):
        config.speed_mode = not config.speed_mode

    def force_update_checkbox_changed(_e):
        config.force_update = (config.force_update + 1) % 2

    def difficult_changed(e: ControlEvent):
        config.difficult = e.data

    def fate_changed(e: ControlEvent):
        config.fate = e.data

    def timezone_changed(e: ControlEvent):
        config.timezone = e.data

    def textbox_changed(e):
        config.order_text = e.control.value

    def get_info_mode(d):
        ls = [False, True, None]
        return ls[d]
    
    def go_money(e=None):
        dlg = ft.AlertDialog(
            title=ft.Text("送杯咖啡喵 QWQ"), content=ft.Image("imgs/money.jpg")
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

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
                                            value=get_info_mode(config.show_map_mode),
                                            on_change=show_map_checkbox_changed,
                                        ),
                                        ft.Checkbox(
                                            label="调试模式",
                                            value=get_info_mode(config.debug_mode),
                                            on_change=debug_checkbox_changed,
                                        ),
                                        ft.Checkbox(
                                            label="速通模式",
                                            value=get_info_mode(config.speed_mode),
                                            on_change=speed_checkbox_changed,
                                        ),
                                        ft.Checkbox(
                                            label="强制更新",
                                            value=get_info_mode(config.force_update),
                                            on_change=force_update_checkbox_changed,
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
                                                ft.dropdown.Option("繁育"),
                                            ],
                                            value=config.fate,
                                            on_change=fate_changed,
                                        ),
                                        ft.Dropdown(
                                            width=150,
                                            label="时区",
                                            hint_text="影响计数刷新时间",
                                            options=[
                                                ft.dropdown.Option("Default"),
                                                ft.dropdown.Option("Asia"),
                                                ft.dropdown.Option("America"),
                                                ft.dropdown.Option("Europe"),
                                            ],
                                            value=config.timezone,
                                            on_change=timezone_changed,
                                        ),
                                    ]
                                ),
                                ft.ElevatedButton(
                                    "赞赏",
                                    icon=ft.icons.THUMB_UP,
                                    on_click=go_money,
                                    width=150,
                                    height=50
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    height=200,
                ),
            ],
            padding=20,
            spacing=0,
        )
    )
