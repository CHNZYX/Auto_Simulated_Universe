[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)


# Auto_Simulated_Universe
Star Rail - Auto Simulated Universe

This project incorporates a pause-resume feature. You can switch to other tasks and return later to continue the automation process.

Currently supports automation of all worlds within the simulated universe.

----------------------------------------------------------------------------------------------

## Disclaimer
This software is an external tool intended to automate gameplay in the game "Honkai Star Rail." It is designed to interact with the game solely through existing user interfaces and in compliance with relevant laws and regulations. This software package aims to provide simplification and user interaction with the game's features and does not intend to disrupt game balance or provide any unfair advantages. The package will not modify any game files or game code in any way.

This software is open-source and free of charge, intended for educational and collaborative purposes only. The development team holds the final interpretation rights for this project. Any issues arising from the use of this software are unrelated to this project and the development team. If you come across merchants using this software for power-leveling and charging for it, the costs might involve equipment and time, and any issues or consequences arising from this software are unrelated to it.

Please note that according to MiHoYo's [Fair Play Declaration for Honkai Star Rail](https://hsr.hoyoverse.com/en-us/news/111244):

    "The use of plug-ins, accelerators, scripts, or other third-party tools that disrupt the fairness of the game is strictly prohibited."
    "Once discovered, miHoYo (hereinafter referred to as 'we') will take measures such as deducting illegal gains, freezing game accounts, and permanently banning game accounts based on the severity and frequency of violations."

### Usage

Only supports 1920x1080 resolution (windowed or fullscreen), turn off hdr, and text language selection is simplified Chinese.

Default World: For instance, if your current default world in the simulated universe is World 4 but you want to automate World 6, please enter World 6 once to change the default world.

If you're not familiar with Python, it's recommended to directly download the GUI version from the [release](https://github.com/CHNZYX/Auto_Simulated_Universe/releases/latest) and follow the GUI usage instructions.

**First-time Setup**

Double-click `install_requirements.bat` to install the required libraries.

Rename `info_example.yml` to `info.yml`.

**Running Automation**

Double-click `run.bat` or run in the command line:
```plaintext
python states.py
```

Detailed parameters:
```plaintext
python states.py --bonus=<bonus> --debug=<debug> --speed=<speed> --find=<find>
```
bonus in [0,1]: Whether to enable immersion bonus.

speed in [0,1]: Enable speedrun mode.

consumable in [0,1]：Enable using the most top-left consumable before elite & boss battle

debug in [0,1,2]: Enable debug mode.

find in [0,1]: 0 for recording, 1 for speedrunning.

The content of `info.yml` is as follows:
```yaml
config:
  order_text: [1, 2, 3, 4] # Character selection order at the start of the simulation. Change this according to your team composition. 1 represents the first character. It's advisable to put ranged characters (like Asta or March 7th) in position 1 for better monster clearing.
  angle: 1.0  # Calibration data, do not modify.
  difficulty: 4 # Universe difficulty, change to 1 if you want to play on difficulty 1.
  fate: 巡猎 # Fate selection, default is 巡猎, you can directly modify it to other fates.
  map_sha: '' # Map data version, not recommended to change.
  show_map_mode: 0
  debug_mode: 0
  speed_mode: 0
  use_consumable: 0
  slow_mode: 0
  force_update: 0
  timezone: Default
prior:
  # Priority information, adjust as needed.
```

The simulation will enter the world that corresponds to the default setting. If your default world is not World 6, remember to manually switch to World 6 first!

Prefer using ranged female characters in the first slot whenever possible. Melee females can also be viable, while other body types (e.g., male characters) may result in stability issues.

Important!!! Once you start running/calibrating, do not move the game window! If you need to move it, please stop the automation first!

**Calibration**

If you're experiencing issues like excessive/inadequate camera rotation leading to getting lost, it might be due to calibration. You can manually calibrate as follows:

Enter the game and teleport your character to Herta's office. Then, double-click `align.bat` and wait for the camera to rotate/character to spin in place.

If `align.bat` crashes, you can try using the command line:
```plaintext
python align_angle.py
```

Changing your mouse DPI might affect calibration values, in which case, you'll need to recalibrate.

**Updating Files**

Double-click `update.bat`.

### GUI Usage Instructions

**First-time Setup**

In the settings, select your desired difficulty and fate. Please pre-select your default team composition in the game.

It's advisable to put a ranged character (like Asta or March 7th) in the first position for better monster clearing.

**Running Automation**

Click the "运行" button.

Important!!! Once you start running/calibrating, do not move the game window! If you need to move it, please stop the automation first!

**TIPS:**

Press F8 or the "停止" button to halt the process.

Prefer using ranged female characters in the first slot whenever possible. Melee females can also be viable, while other body types (e.g., male characters) may result in stability issues.

"显隐" checkbox toggles the visibility of the command-line window. It's hidden by default.

调试模式: If you don't want to exit the settlement after getting lost, please enable debug mode.

If you don't want it to automatically stop after completing 34 rounds, also enable debug mode.

速通模式: Enabling this means you'll only fight the final enemy on each level.

Recommended minimal graphics settings:

![Graphics Settings](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

**Calibration**

If you're experiencing issues like excessive/inadequate camera rotation leading to getting lost, it might be due to calibration. You can manually calibrate as follows:

Enter the game and teleport your character to Herta's office. Then, click the "Calibrate" button, and wait for the camera to rotate/character to spin in place.

Changing your mouse DPI might affect calibration values, in which case, you'll need to recalibrate.

### Update

Double-click `update.exe`.

### Automatic Abyss

Automatic Abyss allows you to use a fixed team to automatically clear the Oblivion Domains, saving time on manual clearing of the initial levels.

To run the script version, use `python abyss.py`. For the GUI version, click the "Abyss" button on the main interface.

For the script version's first run, modify the `info_example.yml` file in the "abyss" folder to `info.yml`, and edit `info.yml` with your two-team composition. In the GUI version, you can input your team composition in the Abyss interface.

Each team's composition is represented by four numbers.

![Team Composition Numbers](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

For instance, in the image above, if you want to choose Natasha, Jing Yuan, Seele, and Yan Qing, input: `6 4 3 2`.

### Notification Plugin Instructions (notif.exe)

If you're not using a local multi-user setup, simply double-click

 `notif.exe` to enable Windows notifications. You'll receive notifications after each completion.

If you're using a local multi-user setup, run the GUI version in the sub-user account and `notif.exe` in the main user account. This way, notifications will be sent to the main user.

The counter resets automatically weekly. If you wish to manually modify the count, open `logs/notif.txt` and edit the first line.

The notification plugin displays a tray icon in the bottom-right corner.

----------------------------------------------------------------------------------------------

### Logic Overview

Blessing selection logic is based on OCR and custom priority settings.

Pathfinding module uses a mini-map.

The mini-map only recognizes white edge lines and yellow interaction points.

----------------------------------------------------------------------------------------------

Support for recording maps is available:

Run `python states.py --debug=2 --find=1`.

If a new map is encountered and your character stops, end the automation and put the game in pause mode in the Simulated Universe.

Then, run `python states.py --debug=2 --find=0`.

The script will automatically enter the map. During this process, do not move the mouse or press any keys.

After a few seconds, the character will move backward and then forward. During the forward movement, you can move the mouse to change the camera angle or use WASD on the keyboard.

Move around the map, and when you feel it's sufficient, press F8 or Ctrl+C to terminate the process. This will capture the map data. It will be saved in the `imgs/maps/my_xxxxx` directory (sorted by modification time).

For maps with monsters, it's advisable to use Seele's ultimate ability. Being locked onto a target can affect the mini-map recognition.

A `target.jpg` file will be present in the `imgs/maps/my_xxxxx` directory. You can use the built-in Paint application on Windows to open it and mark points (you can refer to the `target.jpg` file in other map folders).

Indigo: Path point, Yellow: Destination, Green: Interaction point (question mark), Red: Enemy point

After recording, you can exit the game and re-run the automation to test the map. If the test is successful, you've successfully recorded a new map!

----------------------------------------------------------------------------------------------

Feel free to join and provide feedback. QQ Group: 831830526

----------------------------------------------------------------------------------------------

If you like this project, you can buy the author a cup of coffee!

![Donate](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/money.jpg)
