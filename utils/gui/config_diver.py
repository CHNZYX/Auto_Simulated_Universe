from flet_core import MainAxisAlignment, ControlEvent, CrossAxisAlignment, TextStyle
import flet as ft

from utils.gui.common import show_snack_bar, Page
from utils.diver.config import config
import os


def config_view(page: Page):
    def back_choose(_):
        page.go("/")
        page.update()

    def save(_):
        config.save()
        show_snack_bar(page, "保存成功", ft.colors.GREEN)
        page.go("/")
        page.update()

    def debug_checkbox_changed(_e):
        config.debug_mode = not config.debug_mode

    def speed_checkbox_changed(_e):
        config.speed_mode = not config.speed_mode

    def weekly_checkbox_changed(_e):
        config.weekly_mode = not config.weekly_mode

    def cpu_checkbox_changed(_e):
        config.cpu_mode = not config.cpu_mode

    def difficult_changed(e: ControlEvent):
        config.difficult = e.data

    def save_cnt_changed(e: ControlEvent):
        config.save_cnt = int(e.data)

    def team_changed(e: ControlEvent):
        config.team = e.data

    def timezone_changed(e: ControlEvent):
        config.timezone = e.data

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

    def go_del(e=None):
        try:
            if page.su._stop == 0:
                show_snack_bar(page, "请先退出自动化", ft.colors.RED)
                return
        except:
            pass
        nonlocal txt
        file_name = 'logs/notif.txt'
        cnt='0'
        if os.path.exists(file_name):
            with open(file_name, 'w', encoding="utf-8") as file:
                file.write(f"0\n已清空\n计数:0\n0")
            show_snack_bar(page, "清空成功", ft.colors.GREEN)
            txt.value = '已通关0次'
            page.update()

    def getnum():
        file_name = 'logs/notif.txt'
        cnt='0'
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding="utf-8",errors='ignore') as file:
                    s=file.readlines()
                    cnt=s[0].strip('\n')
            except:
                pass
        return cnt

    txt = ft.Text('已通关'+getnum()+'次',weight=ft.FontWeight.W_600,size=20)
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
                                ft.Column(
                                    [
                                        ft.Container(height=8),
                                        ft.Switch(
                                            label="调试模式",
                                            value=get_info_mode(config.debug_mode),
                                            on_change=debug_checkbox_changed,
                                            label_position='left',
                                            scale=1.2
                                        ),
                                        ft.Switch(
                                            label="速通模式",
                                            value=get_info_mode(config.speed_mode),
                                            on_change=speed_checkbox_changed,
                                            label_position='left',
                                            scale=1.2
                                        ),
                                        ft.Switch(
                                            label="周期演算",
                                            value=get_info_mode(config.weekly_mode),
                                            on_change=weekly_checkbox_changed,
                                            label_position='left',
                                            scale=1.2
                                        ),
                                        ft.Switch(
                                            label="禁用GPU加速",
                                            value=get_info_mode(config.cpu_mode),
                                            on_change=cpu_checkbox_changed,
                                            label_position='left',
                                            scale=1.2,
                                            offset=ft.Offset(x=-0.215,y=0)
                                        ),
                                    ]
                                ),
                                ft.Container(height=20),
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
                                            text_style=TextStyle(color=ft.colors.PINK_600,weight=ft.FontWeight.W_600),
                                            value=config.difficult,
                                            on_change=difficult_changed,
                                        ),
                                        ft.Dropdown(
                                            width=100,
                                            label="存档数量",
                                            hint_text="自动存档数量",
                                            options=[
                                                ft.dropdown.Option("0"),
                                                ft.dropdown.Option("1"),
                                                ft.dropdown.Option("2"),
                                                ft.dropdown.Option("3"),
                                                ft.dropdown.Option("4"),
                                            ],
                                            text_style=TextStyle(color=ft.colors.PINK_600,weight=ft.FontWeight.W_600),
                                            value=config.save_cnt,
                                            on_change=save_cnt_changed,
                                        ),
                                        ft.Dropdown(
                                            width=100,
                                            label="体系",
                                            hint_text="预设队伍体系",
                                            options=[
                                                ft.dropdown.Option("追击"),
                                                ft.dropdown.Option("dot"),
                                                ft.dropdown.Option("终结技"),
                                                ft.dropdown.Option("击破"),
                                                ft.dropdown.Option("盾反"),
                                            ],
                                            text_style=TextStyle(color=ft.colors.PINK_600,weight=ft.FontWeight.W_600),
                                            value=config.team,
                                            on_change=team_changed,
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
                                            text_style=TextStyle(color=ft.colors.PINK_600,weight=ft.FontWeight.W_600),
                                            value=config.timezone,
                                            on_change=timezone_changed,
                                        ),
                                    ]
                                ),
                                ft.Container(height=15),
                                ft.Row(
                                    [
                                        ft.Text("秘技角色:",weight=ft.FontWeight.W_600,size=18),
                                        ft.TextButton(
                                            text='-'.join(config.skill_char),
                                            on_click=lambda _: go_input_y(page),
                                        ),
                                    ]
                                ),
                                ft.Container(height=5),
                                ft.Row(
                                    [
                                        txt,
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            tooltip="清空通关计数",
                                            icon_size=35,
                                            on_click=go_del,
                                        ),
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Text("本轮运行：",weight=ft.FontWeight.W_400,size=18),
                                        ft.TextButton(
                                            text=str(config.max_run),
                                            on_click=lambda _: go_input_x(page),
                                        ),
                                        ft.Text("次",weight=ft.FontWeight.W_400,size=18),
                                    ]
                                ),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.icons.THUMB_UP),
                                            ft.Text("赞赏", weight=ft.FontWeight.W_800, size=16),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
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
                ),
            ],
            padding=20,
            spacing=0,
        )
    )

def go_input_x(page):
    def close_dialog(e, cancel=False):
        if not cancel:
            try:
                new_x = int(textfield_ref.value)
                if 0 <= new_x <= 999 or new_x == -1:
                    config.max_run = new_x
                    x_button.text = str(config.max_run)
                    page.update()
            except:
                pass
        dialog.open = False
        page.update()
    x_button = page.views[-1].controls[-1].controls[-1].controls[-3].controls[1]
    textfield_ref = ft.TextField(
        label="运行次数（-1为无限循环）",
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=close_dialog,
    )
    
    dialog = ft.AlertDialog(
        title=ft.Text("输入运行次数"),
        content=textfield_ref,
        actions=[
            ft.TextButton("取消", on_click=lambda e: close_dialog(e, cancel=True)),
            ft.TextButton("确认", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()

def go_input_y(page):
    def close_dialog(e, cancel=False):
        if not cancel:
            try:
                new_x = str(textfield_ref.value).split('-')
                config.update_skill(new_x)
                x_button.text = '-'.join(config.skill_char)
                page.update()
            except:
                pass
        dialog.open = False
        page.update()
    x_button = page.views[-1].controls[-1].controls[-1].controls[-6].controls[1]
    textfield_ref = ft.TextField(
        label="按输入顺序开角色秘技",
        value='-'.join(config.skill_char),
        keyboard_type=ft.KeyboardType.TEXT,
        on_submit=close_dialog,
    )
    
    dialog = ft.AlertDialog(
        title=ft.Text("秘技角色，用-分隔"),
        content=textfield_ref,
        actions=[
            ft.TextButton("取消", on_click=lambda e: close_dialog(e, cancel=True)),
            ft.TextButton("确认", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()