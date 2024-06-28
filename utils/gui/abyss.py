from flet_core import MainAxisAlignment, ControlEvent, CrossAxisAlignment
import flet as ft

from utils.gui.common import show_snack_bar, Page
import yaml
import traceback
from abyss import Abyss
import os

def abyss_view(page: Page):
    order = ['1 2 3 4','5 6 7 8']
    try:
        with open('abyss/info.yml', "r", encoding="utf-8",errors='ignore') as f:
            config = yaml.safe_load(f)['order_text']
            config = [str(x) for x in config]
            order=[' '.join(config[:4]),' '.join(config[4:])]
    except:
        os.makedirs('abyss', exist_ok=True)
        pass
    
    def back_choose(_):
        try:
            page.ab._stop = 1
        except:
            pass
        page.go("/")
        page.update()

    def start(_e):
        nonlocal order
        order = [x.strip().split(' ') for x in order]
        for i in range(2):
            ls = []
            for j in order[i]:
                try:
                    ls.append(int(j))
                except:
                    pass
            ls += [0,0,0,0]
            order[i] = ls[:4]
        os.makedirs('abyss', exist_ok=True)
        with open('abyss/info.yml', "w", encoding="utf-8") as f:
            yaml.safe_dump({
                    "order_text": order[0] + order[1]
            }, f, allow_unicode=True, sort_keys=False)
        try:
            page.ab._stop = 1
        except:
            pass
        page.ab = Abyss()
        page.ab.start_abyss()

    def stop(_e):
        try:
            page.ab._stop = 1
        except:
            pass
        

    def order_changed1(e):
        nonlocal order
        order[0] = e.control.value
    
    def order_changed2(e):
        nonlocal order
        order[1] = e.control.value


    page.views.append(
        ft.View(
            "/abyss",
            [
                ft.Stack(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(
                                        value="自动忘却之庭",
                                        size=30,
                                    ),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "返回",
                                                icon=ft.icons.ARROW_BACK,
                                                on_click=back_choose,
                                            )
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
                                ft.TextField(
                                    label="配队1",
                                    width=80,
                                    value=order[0],
                                    on_change=order_changed1,
                                ),
                                ft.TextField(
                                    label="配队2",
                                    width=80,
                                    value=order[1],
                                    on_change=order_changed2,
                                ),
                                ft.ElevatedButton(
                                    "保存并开始",
                                    icon=ft.icons.LOGIN,
                                    on_click=start,
                                ),
                                ft.ElevatedButton(
                                    "停止",
                                    icon=ft.icons.STOP,
                                    on_click=stop,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    height=350,
                ),
            ],
            padding=20,
            spacing=0,
        )
    )
