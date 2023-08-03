[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)

[项目文档](https://asu.stysqy.top/)

# Auto_Simulated_Universe
星穹铁道-模拟宇宙全自动化

有一定的断点回复功能，你可以切出去做其他事，切回来会继续自动化。

目前支持模拟宇宙所有世界

----------------------------------------------------------------------------------------------

## 免责声明
本软件是一个外部工具旨在自动化崩坏星轨的游戏玩法。它被设计成仅通过现有用户界面与游戏交互,并遵守相关法律法规。该软件包旨在提供简化和用户通过功能与游戏交互,并且它不打算以任何方式破坏游戏平衡或提供任何不公平的优势。该软件包不会以任何方式修改任何游戏文件或游戏代码。

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

本软件开源、免费，仅供学习交流使用。开发者团队拥有本项目的最终解释权。使用本软件产生的所有问题与本项目与开发者团队无关。若您遇到商家使用本软件进行代练并收费，可能是设备与时间等费用，产生的问题及后果与本软件无关。


请注意，根据MiHoYo的 [崩坏:星穹铁道的公平游戏宣言]([https://hsr.hoyoverse.com/en-us/news/111244](https://sr.mihoyo.com/news/111246?nav=news&type=notice)):

    "严禁使用外挂、加速器、脚本或其他破坏游戏公平性的第三方工具。"
    "一经发现，米哈游（下亦称“我们”）将视违规严重程度及违规次数，采取扣除违规收益、冻结游戏账号、永久封禁游戏账号等措施。"

### 用法

如果你的电脑没有安装python+numpy，或者未正确将python添加进环境变量，那么你将无法使用本项目。请理解本项目设置的这道门槛，如果你被门槛挡住了，请自行百度解决。

只支持1920\*1080(窗口化或全屏幕)，文本语言选择简体中文。（屏幕分辨率等于1920\*1080开全屏幕，大于的开窗口化）

默认世界：比如说如果你当前模拟宇宙默认世界4，但是想自动化世界6，那么请先进入一次世界6来改变默认世界

如果没怎么接触过python，建议直接在[release](https://github.com/CHNZYX/Auto_Simulated_Universe/releases/latest)中下载gui版本，并直接阅读GUI使用方法

**第一次运行**

双击`install_requirements.bat`安装依赖库

进入游戏，将人物传送到黑塔的办公室，然后双击 `align.bat` ，切回游戏界面，等待视角转换/原地转圈结束

如果`align.bat`闪退，可以尝试管理员运行
```plaintext
python align_angle.py
```

如果改变了鼠标dpi或游戏分辨率/屏幕分辨率/窗口缩放倍率，需要重新校准！

**运行自动化**

人物靠近模拟宇宙（出现f键交互条）

双击`run.bat` 或者 管理员权限运行 
```plaintext
python states.py --find=1
```

`info.yml`内容如下
```yaml
config:
  order_text: [1, 2, 3, 4] //模拟宇宙开局选的角色，建议改成自己的配队，1表示第一个角色。最好在一号位选远程角色（艾丝妲、三月七）方便开怪。
  angle: 1.0  //校准数据请勿更改
  difficulty: 4 //宇宙的难度，如果你要打难度1就改成1保存
  fate: 巡猎 //命途选择，默认巡猎，可以直接修改为其它命途，对巡猎做了专门优化，因此除非万不得已不要改命途。
  map_sha: '' //地图数据的版本，不建议更改
  show_map_mode: 0
  debug_mode: 0
  speed_mode: 0
  force_update: 0
  timezone: Default
```

默认是哪个宇宙就会进哪个！如果你默认不是第6世界，记得先手动切到第6世界！

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**更新文件**

双击`update.bat`


### GUI使用方法

**第一次运行**

进入游戏，将人物传送到黑塔的办公室，然后点击校准，等待视角转换/原地转圈结束并弹出校准成功。

如果改变了鼠标dpi或游戏分辨率/屏幕分辨率/窗口缩放倍率，需要重新校准！

在设置中选择自己想要的难度和命途，配队请用三个空格隔开四个数字，1表示第一个角色（编号规则示意见下图）。最好在一号位选远程角色（艾丝妲、三月七）方便开怪。

![配队编号](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

比如说这张图中，你想选择娜塔莎，景元，希儿，彦卿，那么请在配队中输入：`6 4 3 2`

**运行自动化**

人物靠近模拟宇宙（出现f键交互条）

点击运行

注意！！！！！ 开始运行/开始校准之后就不要移动游戏窗口了！要移动请先停止自动化！

**TIPS：**

F8/‘停止’按钮停止运行。

显隐表示显示/隐藏命令行窗口，默认隐藏

调试模式：√表示迷路后不再结算，—表示在√的基础上遇到相似度低的地图会暂停运行

如果不希望迷路后退出结算，请将调试模式变为√

速通模式：√表示只打每层最后一个怪，—表示在√的基础上开启奔跑

左下角为更新地图按钮（只会更新地图，不会更新本体）

录制地图参见后文

推荐最低画质配置：

![画质](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

### 通知插件使用方法（notif.exe）

如果你没有用本地多用户，那么直接双击`notif.exe`即可开启windows通知，每刷完一次都会通知哦

如果你用了本地多用户，那么请在子用户运行gui，在主用户运行notif，这样就能在主用户收到通知了

计数会在每周自动重置，如果想手动改变计数，请打开`logs/notif.txt`，修改第一行的信息

通知插件会在右下角显示托盘图标

----------------------------------------------------------------------------------------------

### 部分逻辑

选祝福的逻辑是硬选巡猎，事件基本都会跳过，最后一层不会强化祝福，奇物随机选。

寻路模块基于小地图

小地图中只会识别白色边缘线和黄色交互点。

----------------------------------------------------------------------------------------------

支持录制地图，具体方法为

运行 `python states.py --debug=2 --find=1` （GUI版本：设置调试模式为-，然后点击运行）

如果遇到新图会角色停住，这时候结束自动化并且游戏中暂离模拟宇宙

然后运行 `python states.py --debug=2 --find=0` （GUI版本：设置调试模式为-，然后点击录制）

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
