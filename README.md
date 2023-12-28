[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)

# Auto_Simulated_Universe
星穹铁道-模拟宇宙全自动化

快速上手，请访问：[项目文档](https://asu.stysqy.top/) [备用](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/index.md)

遇到问题，请在提问前查看：[Q&A](https://asu.stysqy.top/guide/qa.html) [备用](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/qa.md)

运行自动化时不能用电脑做其他事？试试多用户后台运行！[后台运行](https://asu.stysqy.top/guide/bs.html) [备用](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/bs.md)

----------------------------------------------------------------------------------------------

## 免责声明
本软件是一个外部工具旨在自动化崩坏星轨的游戏玩法。它被设计成仅通过现有用户界面与游戏交互,并遵守相关法律法规。该软件包旨在提供简化和用户通过功能与游戏交互,并且它不打算以任何方式破坏游戏平衡或提供任何不公平的优势。该软件包不会以任何方式修改任何游戏文件或游戏代码。

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

本软件开源、免费，仅供学习交流使用。开发者团队拥有本项目的最终解释权。使用本软件产生的所有问题与本项目与开发者团队无关。若您遇到商家使用本软件进行代练并收费，可能是设备与时间等费用，产生的问题及后果与本软件无关。


请注意，根据MiHoYo的 [崩坏:星穹铁道的公平游戏宣言]([https://hsr.hoyoverse.com/en-us/news/111244](https://sr.mihoyo.com/news/111246?nav=news&type=notice)):

    "严禁使用外挂、加速器、脚本或其他破坏游戏公平性的第三方工具。"
    "一经发现，米哈游（下亦称“我们”）将视违规严重程度及违规次数，采取扣除违规收益、冻结游戏账号、永久封禁游戏账号等措施。"

## 安装GUI [![](https://img.shields.io/github/downloads/CHNZYX/Auto_Simulated_Universe/total?color=66ccff)](https://github.com/CHNZYX/Auto_Simulated_Universe/releases)

## 命令行用法

只支持1920\*1080(窗口化或全屏幕)，关闭hdr，文本语言选择简体中文。代码版[下载链接](https://github.com/CHNZYX/Auto_Simulated_Universe/archive/refs/heads/main.zip)

默认世界：比如说如果你当前模拟宇宙默认世界4，但是想自动化世界6，那么请先进入一次世界6来改变默认世界

如果没怎么接触过python，建议直接在[release](https://github.com/CHNZYX/Auto_Simulated_Universe/releases/latest)中下载gui版本，并直接阅读GUI使用方法

**第一次运行**

双击`install_requirements.bat`安装依赖库

重命名info_example.yml为info.yml

**运行自动化**

双击`run.bat` 或者 命令行运行 
```plaintext
python states.py
```

详细参数：
```plaintext
python states.py --bonus=<bonus> --debug=<debug> --speed=<speed> --find=<find> --nums=<nums>
```
bonus in [0,1]：是否开启沉浸奖励

speed in [0,1]：开启速通模式

consumable in [0,1]：精英和首领战之前是否使用最左上角的消耗品

debug in [0,1,2]：开启调试模式

find in [0,1]：0为录图，1为跑图

nums：指定通关次数，必须为正整数

----------------------------------------------------------------------------------------------

`info.yml`内容如下
```yaml
config:
  order_text: [1, 2, 3, 4] //模拟宇宙开局选的角色，建议改成自己的配队，1表示第一个角色。最好在一号位选远程角色（艾丝妲、三月七）方便开怪。
  angle: 1.0  //校准数据请勿更改
  difficulty: 4 //宇宙的难度，如果你要打难度1就改成1保存
  fate: 巡猎 //命途选择，默认巡猎，可以直接修改为其它命途。
  map_sha: '' //地图数据的版本，不建议更改
  show_map_mode: 0
  debug_mode: 0
  speed_mode: 0
  use_consumable: 0
  slow_mode: 0
  force_update: 0
  timezone: Default
prior:
  优先级信息，按需调整
```

use_consumable：0代表不使用消耗品，1代表最终boss使用消耗品，2代表最后两个boss使用消耗品，3代表所有boss都使用消耗品

自动使用第一个攻击/防御消耗品，可以收藏消耗品（星星标记）来改变背包中消耗品的顺序

默认是哪个宇宙就会进哪个！如果你默认不是第6世界，记得先手动切到第6世界！

尽量使用远程成女角色作为一号位，其他体型也能适配。

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**校准**

如果出现视角转动过大/过小而导致迷路的问题，可能是校准值出问题了，可以尝试手动校准：

进入游戏，将人物传送到黑塔的办公室，然后双击 `align.bat`，等待视角转换/原地转圈结束

如果`align.bat`闪退，可以尝试命令行
```plaintext
python align_angle.py
```

改变鼠标dpi可能会影响校准值，此时需要重新校准。

**更新文件**

双击`update.bat`


## GUI使用方法

**第一次运行**

在设置中选择自己想要的难度和命途，配队请在游戏中预先选择默认配队

最好在一号位选远程角色（艾丝妲、三月七等）方便开怪。

**运行自动化**

点击运行

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**TIPS：**

尽量使用远程成女角色作为一号位，近战成女也能适配，其它体型（成男等）会出现稳定性问题。

F8/‘停止’按钮停止运行。

显隐表示显示/隐藏命令行窗口，默认隐藏

调试模式：如果不希望迷路后退出结算，请开启调试模式

如果不希望打完34次后自动停止，也请开启调试模式

速通模式：开启表示只打每层最后一个怪

推荐最低画质配置：

![画质](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

**校准**

如果出现视角转动过大/过小而导致迷路的问题，可能是校准值出问题了，可以尝试手动校准：

进入游戏，将人物传送到黑塔的办公室，然后点击校准，等待视角转换/原地转圈结束

改变鼠标dpi可能会影响校准值，此时需要重新校准。

## 更新

双击update.exe

## 自动深渊

自动深渊可以使用固定配队自动刷忘却之庭，这项功能的目的是节省手动刷前几层的时间。

代码版启动方法为`python abyss.py`，gui版启动方法为主界面中的“深渊”按钮。

代码版第一次运行需要修改abyss文件夹下的info_example.yml为info.yml，并且修改info.yml为自己的两队配队，gui版可以在深渊界面中输入自己的配队。

每队的配队信息为四个数字

![配队编号](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

比如说这张图中，你想选择娜塔莎，景元，希儿，彦卿，那么请在配队中输入：`6 4 3 2`

## 通知插件使用方法（notif.exe）

如果你没有用本地多用户，那么直接双击`notif.exe`即可开启windows通知，每刷完一次都会通知哦

如果你用了本地多用户，那么请在子用户运行gui，在主用户运行notif，这样就能在主用户收到通知了

计数会在每周自动重置，如果想手动改变计数，请打开`logs/notif.txt`，修改第一行的信息

通知插件会在右下角显示托盘图标

----------------------------------------------------------------------------------------------

## 部分逻辑

选择祝福的逻辑基于ocr+自定义优先级

寻路模块基于小地图

小地图中只会识别白色边缘线和黄色交互点。

----------------------------------------------------------------------------------------------

支持录制地图，具体方法为

运行 `python states.py --debug --find=1`

如果遇到新图会角色停住，这时候结束自动化并且游戏中暂离模拟宇宙

然后运行 `python states.py --debug --find=0`

运行后会自动进入地图，期间请不要移动鼠标也不要动键盘

几秒后角色会后退，然后前进。在角色前进时，你可以移动鼠标改变视角，也可以按键盘wasd。

在地图中绕一圈，感觉差不多就`F8/ctrl+c`结束进程能得到地图数据了。保存在`imgs/maps/my_xxxxx`目录下（可以按修改时间排序）

有怪的图最好用希儿战技，被锁定会影响小地图识别。

`imgs/maps/my_xxxxx`目录下会存在`target.jpg`，你可以用windows自带的画图打开它，然后在上面标记点（可以参考其它地图文件中的`target.jpg`）

靛蓝色：路径点 黄色：终点 绿色：交互点（问号点） 红色：怪点

录制结束后可以暂离并重新运行自动化测试地图，如果通过测试，你就成功录制到了新图！

----------------------------------------------------------------------------------------------

欢迎加入，欢迎反馈bug，QQ群：831830526

----------------------------------------------------------------------------------------------

如果喜欢本项目，可以打赏送作者一杯咖啡喵！

![打赏](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/money.jpg)

----------------------------------------------------------------------------------------------
## 贡献者

感谢以下贡献者对本项目做出的贡献

<a href="https://github.com/CHNZYX/Auto_Simulated_Universe/graphs/contributors">

  <img src="https://contrib.rocks/image?repo=CHNZYX/Auto_Simulated_Universe" />

</a>

![Alt](https://repobeats.axiom.co/api/embed/a24da575ebc375e58ec8d8a0d7fff6d26306d2fc.svg "Repobeats analytics image")

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CHNZYX/Auto_Simulated_Universe&type=Date)](https://star-history.com/#CHNZYX/Auto_Simulated_Universe&Date)
