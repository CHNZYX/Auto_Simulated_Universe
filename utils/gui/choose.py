import traceback

import flet as ft
import win32gui
from flet_core import MainAxisAlignment, CrossAxisAlignment

from align_angle import main as align_angle
from utils.gui.common import show_snack_bar, Page, list_handles
from simul import SimulatedUniverse
from diver import DivergentUniverse, version
from utils.diver.config import config as config_diver
from utils.simul.config import config as config_simul
from utils.simul.update_map import update_map
from utils.simul.utils import notif
from utils.diver.args import args
from utils.log import my_print as print
from utils.log import print_exc
import time


def choose_view(page: Page):
    def change_all_button(value: bool = True):
        cnt = 0
        for i in page.views[0].controls[0].controls:
            if isinstance(i, ft.FilledButton):
                if cnt <= 1:
                    i.disabled = value
                    cnt += 1
                else:
                    i.disabled = False
        page.update()

    def run(func, *args, **kwargs):
        try:
            change_all_button()
            res = func(*args, **kwargs)
            change_all_button(False)
            return res
        except Exception:
            print("E: 运行函数时出现错误")
            print_exc()
        finally:
            change_all_button(False)

    def angle(_e):
        if config_diver.angle == "1.0" or page.first == 1:
            go_about()
            time.sleep(8)
            page.first = 0
            page.dialog.open = False
            page.update()
        show_snack_bar(page, "开始校准，请切换回游戏（¬､¬）", ft.colors.GREEN)
        res = run(align_angle)
        if res == 1:
            show_snack_bar(page, "校准成功（＾∀＾●）", ft.colors.GREEN)
        else:
            show_snack_bar(page, "校准失败（⊙.⊙）", ft.colors.RED)
        try:
            guind = list_handles('AutoSimulatedUniverse')
            win32gui.SetForegroundWindow(guind)
        except:
            pass

    def start(_e, name):
        if page.first == 1:
            go_about()
            time.sleep(8)
            page.first = 0
            page.dialog.open = False
            page.update()
        show_snack_bar(page, "开始运行，请切换回游戏（＾∀＾●）", ft.colors.GREEN)
        if name == 'simul':
            page.su = run(
                SimulatedUniverse,
                1,
                int(config_simul.debug_mode),
                int(config_simul.show_map_mode),
                int(config_simul.speed_mode),
                int(config_simul.use_consumable),
                int(config_simul.slow_mode),
                int(config_simul.max_run),
                unlock = True,
                bonus=config_simul.bonus,
                gui=1,
            )
        else:
            args.cpu = int(config_diver.cpu_mode)
            page.su = run(
                DivergentUniverse,
                int(config_diver.debug_mode),
                int(config_diver.max_run),
                int(config_diver.speed_mode)
            )
        run(page.su.start)
        txt = " "
        try:
            guind = list_handles('AutoSimulatedUniverse')
            win32gui.SetForegroundWindow(guind)
        except:
            pass
        if page.su is not None:
            run(page.su.stop)
        notif("已退出自动化", txt)

    def start_abyss(_e):
        page.go("/abyss")

    def stops(_e):
        show_snack_bar(page, "停止运行（>∀<）", ft.colors.GREEN)
        try:
            page.su._stop = 1
        except:
            pass
        if page.su is not None:
            run(page.su.stop)

    def update_maps(_e):
        show_snack_bar(page, "更新地图功能已经弃用（´・н・‘）", ft.colors.RED)
        return
        show_snack_bar(page, "开始更新地图（´・н・‘）", ft.colors.GREEN)
        msg, col = update_map(config.force_update)
        show_snack_bar(page, msg, col)

    def go_config(_e, name):
        page.go("/config_"+name)

    def go_about(e=None):
        dlg = ft.AlertDialog(
            title=ft.Text("此程序为免费开源项目，如果你付了钱请立刻退款！"),
            content=ft.Text(
                "咸鱼倒狗4000+！你付给倒狗的每一分钱都会让开源自动化更艰难，请退款并举报商家！本项目已经因倒卖行为受到严重威胁，请帮助我们！\n链接：https://github.com/CHNZYX/Auto_Simulated_Universe\n新群群号：545443061\n10秒后自动关闭"
            ),
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def go_test(e=None):
        args.cpu = int(config_diver.cpu_mode)
        page.su = run(
            DivergentUniverse,
            int(config_diver.debug_mode),
            int(config_diver.max_run),
            int(config_diver.speed_mode)
        )
        run(page.su.screen_test)
        txt = " "
        if page.su is not None:
            run(page.su.stop)
        notif("已完成截图测试", txt)

    def go_money(e=None):
        dlg = ft.AlertDialog(
            title=ft.Text("送杯咖啡喵 QWQ"), content=ft.Image("imgs/money.jpg")
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def go_dep(e=None):
        dlg = ft.AlertDialog(
            title=ft.Text("异常退出"),
            content=ft.Text(" "),  # "请确认python+numpy已安装并正确配置环境变量")
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def unlock(e=None):
        show_snack_bar(page, "解锁限制功能已经弃用o(*￣▽￣*)ブ", ft.colors.RED)
        return
        go_money()
        time.sleep(3)
        page.dialog.open = False
        page.update()
        show_snack_bar(page, "稍后解锁限制，赞助页面在右下角按钮~o( =∩ω∩= )m", ft.colors.GREEN)
        time.sleep(7)
        config.unlock = 1
        show_snack_bar(page, "已临时解锁限制o(*￣▽￣*)ブ", ft.colors.GREEN)

    def bonus_changed(e):
        config_simul.bonus = not config_simul.bonus

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
                                version+' by CHNZYX',
                                size=20,
                            ),
                        ),
                        ft.Container(
                            content=ft.Text(
                                "开源免费，任何收费行为均为倒卖！",
                                size=20,
                            ),
                        ),
                        ft.Container(),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.ADD_TASK),
                                    ft.Text("校准", weight=ft.FontWeight.W_600),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                            on_click=angle,
                            width=120,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.INFO),
                                    ft.Text("关于", weight=ft.FontWeight.W_600),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                            on_click=go_about,
                            width=120,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.STOP),
                                    ft.Text("停止", weight=ft.FontWeight.W_600),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                            on_click=stops,
                            width=120,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.TRACK_CHANGES),
                                    ft.Text("测试", weight=ft.FontWeight.W_600),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            ),
                            on_click=go_test,
                            width=120,
                        ),
                        ft.Container(height=5),
                        ft.Row([
                            ft.Column([
                                ft.Text("模拟宇宙", size=18, weight=ft.FontWeight.W_600, offset=ft.Offset(x=0.3, y=0), color=ft.colors.PINK_600),
                                ft.Container(),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.icons.LOGIN),
                                            ft.Text("运行", weight=ft.FontWeight.W_600),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                    on_click=lambda e: start(e, 'simul'),
                                    width=120,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.icons.SETTINGS),
                                            ft.Text("设置", weight=ft.FontWeight.W_700),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                    on_click=lambda e: go_config(e, 'simul'),
                                    width=120,
                                ),
                            ]),
                            ft.Container(width=100),
                            ft.Column([
                                ft.Text("差分宇宙", size=18, weight=ft.FontWeight.W_600, offset=ft.Offset(x=0.3, y=0), color=ft.colors.PINK_600),
                                ft.Container(),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.icons.LOGIN),
                                            ft.Text("运行", weight=ft.FontWeight.W_600),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                    on_click=lambda e: start(e, 'diver'),
                                    width=120,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.icons.SETTINGS),
                                            ft.Text("设置", weight=ft.FontWeight.W_700),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                    on_click=lambda e: go_config(e, 'diver'),
                                    width=120,
                                ),
                            ]),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Container(width=630),
                        ft.IconButton(
                            icon=ft.icons.THUMB_UP,
                            tooltip="赞赏",
                            icon_size=35,
                            on_click=go_money,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    vertical_alignment=CrossAxisAlignment.END,
                ),
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            vertical_alignment=MainAxisAlignment.CENTER,
        )
    )
