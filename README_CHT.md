[簡體中文](README.md) | [繁體中文](README_CHT.md) | [English](README_ENG.md)

# Auto_Simulated_Universe
星穹鐵道-模擬宇宙全自動化

有一定的斷點回復功能，你可以切出去做其他事，切回來會繼續自動化。

目前支持模擬宇宙所有世界

----------------------------------------------------------------------------------------------

## 免責聲明
本軟件是一個外部工具旨在自動化崩壞星軌的遊戲玩法。它被設計成僅通過現有用戶界面與遊戲交互,並遵守相關法律法規。該軟件包旨在提供簡化和用戶通過功能與遊戲交互,並且它不打算以任何方式破壞遊戲平衡或提供任何不公平的優勢。該軟件包不會以任何方式修改任何遊戲文件或遊戲代碼。

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

本軟件開源、免費，僅供學習交流使用。開發者團隊擁有本項目的最終解釋權。使用本軟件產生的所有問題與本項目與開發者團隊無關。若您遇到商家使用本軟件進行代練並收費，可能是設備與時間等費用，產生的問題及後果與本軟件無關。


請註意，根據MiHoYo的 [崩壞:星穹鐵道的公平遊戲宣言]([https://hsr.hoyoverse.com/en-us/news/111244](https://sr.mihoyo.com/news/111246?nav=news&type=notice)):

    "嚴禁使用外掛、加速器、腳本或其他破壞遊戲公平性的第三方工具。"
    "一經發現，米哈遊（下亦稱「我們」）將視違規嚴重程度及違規次數，采取扣除違規收益、凍結遊戲賬號、永久封禁遊戲賬號等措施。"

### 用法

只支持1920\*1080(窗口化或全屏幕)，關閉hdr，文本語言選擇簡體中文。

默認世界：比如說如果你當前模擬宇宙默認世界4，但是想自動化世界6，那麽請先進入一次世界6來改變默認世界

如果沒怎麽接觸過python，建議直接在[release](https://github.com/CHNZYX/Auto_Simulated_Universe/releases/latest)中下載gui版本，並直接閱讀GUI使用方法

**第一次運行**

雙擊`install_requirements.bat`安裝依賴庫

重命名info_example.yml為info.yml

**運行自動化**

雙擊`run.bat` 或者 命令行運行 
```plaintext
python states.py
```

詳細參數：
```plaintext
python states.py --bonus=<bonus> --debug=<debug> --speed=<speed> --find=<find>
```
bonus in [0,1]：是否開啟沈浸獎勵

speed in [0,1]：開啟速通模式

consumable in [0,1]：菁英和首領戰之前是否使用最左上角的消耗品

debug in [0,1,2]：開啟調試模式

find in [0,1]：0為錄圖，1為跑圖

----------------------------------------------------------------------------------------------

`info.yml`內容如下
```yaml
config:
  order_text: [1, 2, 3, 4] //模擬宇宙開局選的角色，建議改成自己的配隊，1表示第一個角色。最好在一號位選遠程角色（艾絲妲、三月七）方便開怪。
  angle: 1.0  //校準數據請勿更改
  difficulty: 4 //宇宙的難度，如果你要打難度1就改成1保存
  fate: 巡獵 //命途選擇，默認巡獵，可以直接修改為其它命途。
  map_sha: '' //地圖數據的版本，不建議更改
  show_map_mode: 0
  debug_mode: 0
  speed_mode: 0
  use_consumable: 0
  slow_mode: 0
  force_update: 0
  timezone: Default
prior:
  優先級信息，按需調整
```

默認是哪個宇宙就會進哪個！如果你默認不是第6世界，記得先手動切到第6世界！

盡量使用遠程成女角色作為一號位，近戰成女也能適配，其它體型（成男等）會出現穩定性問題。

註意！！！！！ 開始運行/開始校準之後就不要移動遊戲窗口了！要移動請先停止自動化！

**校準**

如果出現視角轉動過大/過小而導致迷路的問題，可能是校準值出問題了，可以嘗試手動校準：

進入遊戲，將人物傳送到黑塔的辦公室，然後雙擊 `align.bat`，等待視角轉換/原地轉圈結束

如果`align.bat`閃退，可以嘗試命令行
```plaintext
python align_angle.py
```

改變鼠標dpi可能會影響校準值，此時需要重新校準。

**更新文件**

雙擊`update.bat`


### GUI使用方法

**第一次運行**

在設置中選擇自己想要的難度和命途，配隊請在遊戲中預先選擇默認配隊

最好在一號位選遠程角色（艾絲妲、三月七等）方便開怪。

**運行自動化**

點擊運行

註意！！！！！ 開始運行/開始校準之後就不要移動遊戲窗口了！要移動請先停止自動化！

**TIPS：**

盡量使用遠程成女角色作為一號位，近戰成女也能適配，其它體型（成男等）會出現穩定性問題。

F8/『停止』按鈕停止運行。

顯隱表示顯示/隱藏命令行窗口，默認隱藏

調試模式：如果不希望迷路後退出結算，請開啟調試模式

如果不希望打完34次後自動停止，也請開啟調試模式

速通模式：開啟表示只打每層最後一個怪

推薦最低畫質配置：

![畫質](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

**校準**

如果出現視角轉動過大/過小而導致迷路的問題，可能是校準值出問題了，可以嘗試手動校準：

進入遊戲，將人物傳送到黑塔的辦公室，然後點擊校準，等待視角轉換/原地轉圈結束

改變鼠標dpi可能會影響校準值，此時需要重新校準。

### 更新

雙擊update.exe

### 自動深淵

自動深淵可以使用固定配隊自動刷忘卻之庭，這項功能的目的是節省手動刷前幾層的時間。

代碼版啟動方法為`python abyss.py`，gui版啟動方法為主界面中的「深淵」按鈕。

代碼版第一次運行需要修改abyss文件夾下的info_example.yml為info.yml，並且修改info.yml為自己的兩隊配隊，gui版可以在深淵界面中輸入自己的配隊。

每隊的配隊信息為四個數字

![配隊編號](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

比如說這張圖中，你想選擇娜塔莎，景元，希兒，彥卿，那麽請在配隊中輸入：`6 4 3 2`

### 通知插件使用方法（notif.exe）

如果你沒有用本地多用戶，那麽直接雙擊`notif.exe`即可開啟windows通知，每刷完一次都會通知哦

如果你用了本地多用戶，那麽請在子用戶運行gui，在主用戶運行notif，這樣就能在主用戶收到通知了

計數會在每周自動重置，如果想手動改變計數，請打開`logs/notif.txt`，修改第一行的信息

通知插件會在右下角顯示托盤圖標

----------------------------------------------------------------------------------------------

### 部分邏輯

選擇祝福的邏輯基於ocr+自定義優先級

尋路模塊基於小地圖

小地圖中只會識別白色邊緣線和黃色交互點。

----------------------------------------------------------------------------------------------

支持錄製地圖，具體方法為

運行 `python states.py --debug=2 --find=1`

如果遇到新圖會角色停住，這時候結束自動化並且遊戲中暫離模擬宇宙

然後運行 `python states.py --debug=2 --find=0`

運行後會自動進入地圖，期間請不要移動鼠標也不要動鍵盤

幾秒後角色會後退，然後前進。在角色前進時，你可以移動鼠標改變視角，也可以按鍵盤wasd。

在地圖中繞一圈，感覺差不多就`F8/ctrl+c`結束進程能得到地圖數據了。保存在`imgs/maps/my_xxxxx`目錄下（可以按修改時間排序）

有怪的圖最好用希兒戰技，被鎖定會影響小地圖識別。

`imgs/maps/my_xxxxx`目錄下會存在`target.jpg`，你可以用windows自帶的畫圖打開它，然後在上面標記點（可以參考其它地圖文件中的`target.jpg`）

靛藍色：路徑點 黃色：終點 綠色：交互點（問號點） 紅色：怪點

錄製結束後可以暫離並重新運行自動化測試地圖，如果通過測試，你就成功錄製到了新圖！

----------------------------------------------------------------------------------------------

歡迎加入，歡迎反饋bug，QQ群：831830526

----------------------------------------------------------------------------------------------

![打賞](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/money.jpg)
