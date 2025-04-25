[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)

# Auto_Simulated_Universe
星穹铁道-模拟宇宙全自动化

快速上手，请访问：[项目文档](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/index.md)

遇到问题，请在提问前查看：[Q&A](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/qa.md)

运行自动化时不能用电脑做其他事？试试多用户后台运行！[后台运行](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/bs.md)

此页面主要介绍差分宇宙自动化，如需详细的普通模拟宇宙自动化介绍请移步[普通宇宙](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/old/README.md)

----------------------------------------------------------------------------------------------

## 免责声明
本软件是一个外部工具旨在自动化崩坏星轨的游戏玩法。它被设计成仅通过现有用户界面与游戏交互,并遵守相关法律法规。该软件包旨在提供简化和用户通过功能与游戏交互,并且它不打算以任何方式破坏游戏平衡或提供任何不公平的优势。该软件包不会以任何方式修改任何游戏文件或游戏代码。

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

本软件开源、免费，仅供学习交流使用。开发者团队拥有本项目的最终解释权。使用本软件产生的所有问题与本项目与开发者团队无关。若您遇到商家使用本软件进行代练并收费，可能是设备与时间等费用，产生的问题及后果与本软件无关。


请注意，根据MiHoYo的 [崩坏:星穹铁道的公平游戏宣言]([https://hsr.hoyoverse.com/en-us/news/111244](https://sr.mihoyo.com/news/111246?nav=news&type=notice)):

    "严禁使用外挂、加速器、脚本或其他破坏游戏公平性的第三方工具。"
    "一经发现，米哈游（下亦称“我们”）将视违规严重程度及违规次数，采取扣除违规收益、冻结游戏账号、永久封禁游戏账号等措施。"

## 安装GUI [![](https://img.shields.io/github/downloads/CHNZYX/Auto_Simulated_Universe/total?color=66ccff)](https://github.com/CHNZYX/Auto_Simulated_Universe/releases)

\[新增\]: v7.2后支持云·星穹铁道。云崩铁要用网页应用打开，直接在网页打开会无法识别。需要关闭网速和延迟显示；同时需要设置为全屏幕，并且物理屏幕分辨率为x\*1080(x>=1920)。若无法达到要求，建议在多用户下开启。

## 命令行用法

只支持x\*1080(x>=1920,窗口化或全屏幕)，关闭hdr，文本语言选择简体中文，游戏界面不能有任何遮挡。代码版[下载链接](https://github.com/CHNZYX/Auto_Simulated_Universe/archive/refs/heads/main.zip)

如果没怎么接触过python，建议直接在[release](https://github.com/CHNZYX/Auto_Simulated_Universe/releases/latest)中下载gui版本，并直接阅读GUI使用方法

**第一次运行**

建议使用anaconda，创建虚拟环境并安装依赖库（conda需要在cmd下运行，powershell可能无法切换虚拟环境）

```plaintext
conda create -n asu python=3.12 -y
conda activate asu
pip install -r requirements.txt
```

或者直接安装（不建议）：双击`install_requirements.bat`安装依赖库

重命名info_example.yml为info.yml

**运行自动化**

命令行运行

差分宇宙
```plaintext
python diver.py
```

或普通模拟宇宙
```plaintext
python simul.py
```

详细参数：
```plaintext
python diver.py <--debug> <--speed> <--cpu> --nums=<nums>
```
--speed：开启速通模式

--debug：开启调试模式

--cpu：图像识别强制使用cpu

nums：指定通关次数，必须为正整数

```plaintext
python simul.py --bonus=<bonus> --debug=<debug> --speed=<speed> --find=<find> --nums=<nums>
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
  # 难度，1-5，（5代表最高难度，如果世界没有难度5则会选择难度4）
  difficulty: 5
  # 队伍类型 目前只支持：追击/dot/终结技/击破/盾反
  team: 终结技
  # 速通模式
  speed_mode: 0
  # 图像识别强制使用cpu
  cpu_mode: 0
  # 首领房间需要开秘技的角色，按顺序开
  skill:
    - 黄泉
  # 自动存档数量，0-4，0代表不存档，1-4代表自动存档到前1-4个存档位
  save: 4
  timezone: Default
  max_run: 34
```

必须携带至少一名远程平a角色，最好放在1号位

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**校准**

如果出现视角转动过大/过小而导致迷路的问题，可能是校准值出问题了，可以尝试手动校准：

进入游戏，将人物传送到黑塔的办公室，然后命令行运行 `python align_angle.py`，等待视角转换/原地转圈结束

改变鼠标dpi可能会影响校准值，此时需要重新校准。

## GUI使用方法

**第一次运行**

在游戏中设置“自动沿用战斗设置”

**运行自动化**

点击运行

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**TIPS：**

尽量使用远程角色作为一号位，队伍中必须至少有一名远程角色。

F8/‘停止’按钮停止运行。

显隐表示显示/隐藏命令行窗口，默认隐藏

调试模式：如果不希望迷路后退出结算，请开启调试模式

速通模式：开启表示追求最高效率通关，低配队伍慎用

推荐最低画质配置：

![画质](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

**校准**

如果出现视角转动过大/过小而导致迷路的问题，可能是校准值出问题了，可以尝试手动校准：

进入游戏，将人物传送到黑塔的办公室，然后点击校准，等待视角转换/原地转圈结束

改变鼠标dpi可能会影响校准值，此时需要重新校准。

## 更新

~~双击update.exe~~

## 通知插件使用方法（notif.exe）

如果你没有用本地多用户，那么直接双击`notif.exe`即可开启windows通知，每刷完一次都会通知哦

如果你用了本地多用户，那么请在子用户运行gui，在主用户运行notif，这样就能在主用户收到通知了

计数会在每周自动重置，如果想手动改变计数，请打开`logs/notif.txt`，修改第一行的信息

通知插件会在右下角显示托盘图标

----------------------------------------------------------------------------------------------

~~欢迎加入，欢迎反馈bug，QQ群：831830526~~

~~群没了，可以加736265667~~

二群545443061

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
