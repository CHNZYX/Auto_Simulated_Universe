[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)


# Auto_Simulated_Universe
Star Rail - Auto Simulated Universe

Features a pause-resume function that allows you to switch tasks and return to continue automation.

Supports all worlds in the Simulated Universe as of now.

----------------------------------------------------------------------------------------------

## Disclaimer
This software is an external tool designed to automate gameplay in the game Honkai Star Rail. It interacts with the game solely through existing user interfaces and complies with relevant laws and regulations. The purpose of this software package is to simplify and enhance user interaction with the game through its functionality. It is not intended to disrupt game balance or provide any unfair advantages. This software package does not modify any game files or game code.

This software is open-source, free of charge, and intended for learning and exchange purposes only. The developer team holds the final authority to interpret this project. Any issues arising from the use of this software are unrelated to this project and its developer team. If you encounter merchants using this software for services and charging fees, it might be due to equipment and time costs. Any issues and consequences resulting from such usage are not related to this software.

Please note that according to MiHoYo's [Fair Play Pledge for Honkai Star Rail](https://sr.mihoyo.com/news/111246?nav=news&type=notice):

    "The use of third-party tools such as plugins, accelerators, scripts, or other tools that disrupt game fairness is strictly prohibited."
    "Upon discovery, miHoYo (referred to as 'we' hereinafter) will take measures including deduction of illegal gains, freezing of game accounts, and permanent bans, depending on the seriousness and frequency of the violations."

### Usage

This tool currently supports screen resolutions of 1920x1080 (windowed or fullscreen), detailed descriptions enabled for blessings, and Simplified Chinese selected as the text language.

Default world: If, for example, your current default Simulated Universe world is set to World 4, but you want to automate actions in World 6, please enter World 6 once to update the default world.

If you're not familiar with Python, it's recommended to directly download the GUI version from the latest release and follow the GUI usage instructions.

**Initial Setup**

Double-click `install_requirements.bat` to install the required libraries.

Enter the game and teleport the character to Herta's office. Then double-click `align.bat`, switch back to the game interface, and wait for the camera angle transition or spinning to complete.

If `align.bat` crashes, you can try running the following command as an administrator:

```plaintext
python align_angle.py
```

If you've changed your mouse DPI or the game resolution/screen resolution/window scaling ratio, recalibration is necessary!

**Running Automation**

Position your character near the Simulated Universe (when the F key interaction prompt appears).

Double-click `run.bat` or run with administrator privileges:

```plaintext
python states.py --find=1
```

The content of `info.yml` is as follows:
```yaml
config:
  order_text: [1, 2, 3, 4] // the characters chosen for the simulation universe. Customize your team composition by assigning numbers to characters, where 1 represents the first character. It's recommended to select a ranged character (e.g., Asta or March 7th) for the first position to facilitate initial encounters.
  angle: 1.0 // Calibration data, please avoid modification.
  difficulty: 4 // Universe difficulty level. Change to '1' if you wish to play at difficulty level 1 and then save.
  fate: The Hunt // path selection, default set to "The Hunt." You can directly modify it to another path, but keep in mind that "The Hunt" path is specifically optimized, so it's recommended not to change it unless necessary.
  map_sha: '' // Map data version, not recommended for modification.
  show_map_mode: 0
  debug_mode: 0
  speed_mode: 0
  force_update: 0
  timezone: Default
```

By default, the program will enter the universe corresponding to the default settings. If the default universe is not the 6th world, remember to manually switch to the 6th world first!

**Updating Files**

Double-click on `update.bat`.

### GUI Usage

**Initial Setup**

Enter the game and teleport your character to Herta's office. Then click on "Calibration" and wait for the camera angle to transition or for the character to complete spinning in place. A calibration success message will appear.

If you change your mouse DPI or the game resolution/screen resolution/window scaling factor, recalibration is necessary!

In the settings, choose the desired difficulty and path. For team composition, input four numbers separated by spaces, where 1 represents the first character (see the figure below for the numbering scheme). It's recommended to select a ranged character (e.g., Aisita or San Yue Qi) for the first position to facilitate initial encounters.

![Team Numbering](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

For example, if you want to select Natasha, Jing Yuan, Seele, and Yan Qing, input the following numbers for the team composition: 6 4 3 2

**Running the Automation**

Move your character close to the Simulated Universe (when the "F" key interaction prompt appears).

Click on "Run."

Note: After starting the automation or calibration process, do not move the game window. If you need to move it, please stop the automation first.

**TIPS:**

Press F8 or the "Stop" button to halt automation.

The visibility setting controls whether the command-line window is displayed or hidden. By default, it is hidden.

Debug mode: Check (√) means the program won't exit after getting lost. "—" indicates that the program will also pause if it encounters a map with low similarity.

If you don't want the program to exit after getting lost, change the debug mode to (√).

Speedrun mode: Check (√) means only the last enemy on each floor will be fought. "—" means the program will also enable sprinting, in addition to (√).

The "Update Map" button is located in the lower-left corner (it only updates the map, not the core program).

Refer to the following instructions for recording maps.

Recommended minimum graphics settings:

![Graphics Settings](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

### Notification Plugin Usage (notif.exe)

If you're not using local multiple users, simply double-click on `notif.exe` to enable Windows notifications. You will receive notifications after each completion.

If you're using local multiple users, run the GUI in the child user account and run `notif.exe` in the main user account. This way, notifications will be received in the main user account.

The counter will automatically reset every week. If you want to manually change the counter, open `logs/notif.txt` and modify the information on the first line.

The notification plugin will display a tray icon in the lower-right corner.

----------------------------------------------------------------------------------------------

### Logic Overview

The logic for selecting blessings relies on OCR and custom priority settings.

The pathfinding module is based on the mini-map.

The mini-map

 only recognizes white edge lines and yellow interaction points.

----------------------------------------------------------------------------------------------

Recording maps is supported. The process is as follows:

Run `python states.py --debug=2 --find=1` (GUI version: set debug mode to "-", then click "Run").

If encountering a new map causes the character to stop, end the automation and exit the Simulated Universe in the game.

Then run `python states.py --debug=2 --find=0` (GUI version: set debug mode to "-", then click "Record").

The program will automatically enter the map. During this process, avoid moving the mouse or pressing any keys.

After a few seconds, the character will retreat and then move forward. While the character is moving forward, you can adjust the camera angle with the mouse or use the WASD keys.

Circle around the map until you feel satisfied. Then press F8 or Ctrl+C to end the process and obtain the map data. The data will be saved in the directory `imgs/maps/my_xxxxx` (sorted by modification time).

For maps with enemies, it's recommended to use Xi Er's combat skills, as being locked on can affect mini-map recognition.

In the directory `imgs/maps/my_xxxxx`, you'll find a file named `target.jpg`. You can use Windows' built-in Paint application to open it and mark points on the map (you can refer to the `target.jpg` file in other map files).

Indigo: Path points, Yellow: End point, Green: Interaction point (question mark), Red: Enemy point

After recording, you can exit the Simulated Universe and run automation again to test the map. If the test is successful, you've successfully recorded a new map!

----------------------------------------------------------------------------------------------

Feel free to join us and provide bug feedback. QQ Group: 831830526

----------------------------------------------------------------------------------------------

If you appreciate this project, consider showing your support by buying the author a cup of coffee!

![Support](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/money.jpg)
```

Please review this version and let me know if there are any further adjustments or corrections needed.
