[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_ENG.md)

# Auto_Simulated_Universe
Star Rail - Automated Simulated Universe

It has a breakpoint recovery function, so you can switch to do other things and come back to continue automation.

Currently, only World 4 (incomplete data) and World 6 are supported, and the map data has been mostly recorded.

----------------------------------------------------------------------------------------------

## Disclaimer
This software is an external tool designed to automate gameplay in the game Honkai Star Rail. It is designed to interact with the game only through existing user interfaces and complies with relevant laws and regulations. The purpose of this software package is to provide simplification and user interaction with the game through functionality, and it is not intended to disrupt game balance or provide any unfair advantages. This software package does not modify any game files or game code in any way.

This software is open source, free of charge, and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

Please note that according to MiHoYo's [Fair Play Pledge for Honkai Star Rail](https://sr.mihoyo.com/news/111246?nav=news&type=notice):

    "The use of third-party tools such as plugins, accelerators, scripts, or other tools that disrupt game fairness is strictly prohibited."
    "Upon discovery, miHoYo (hereinafter referred to as "we") will take measures including deduction of illegal gains, freezing of game accounts, and permanent bans, depending on the seriousness and frequency of the violations."

### Usage

If your computer does not have Python + NumPy installed or if Python has not been properly added to the environment variables, you will be unable to use this project. Please understand the threshold set by this project. If you are blocked by this threshold, please search for a solution on Google by yourself.

Only supports 1920\*1080 (windowed or fullscreen), enable detailed descriptions for blessings, and select Simplified Chinese as the text language. (If the screen resolution is equal to 1920\*1080, open in fullscreen; if it is larger, open in windowed mode).

Default world: For example, if your current Simulated Universe is set to default to World 4, but you want to automate World 6, please enter World 6 once to change the default world.

If you are not familiar with Python, it is recommended to directly download the GUI version from the release and read the GUI usage instructions directly.

**First-time Setup**

Double-click `install_requirements.bat` to install the required libraries.

Enter the game and teleport the character to Herta's office. Then double-click `align.bat`, switch back to the game interface, and wait for the camera angle transition or spinning to finish.

If `align.bat` crashes, you can try running the following command as an administrator:

```plaintext
python align_angle.py
```

If you have changed the mouse DPI or the game resolution/screen resolution/window scaling ratio, you need to recalibrate!

**Running Automation**

Character close to the Simulated Universe (F key interaction prompt appears).

Double-click `run.bat` or run with administrator privileges:

```plaintext
python states.py --find=1
```
The first line in `info.txt` stores the character chosen for the simulation universe. It is recommended to customize your own team composition by assigning numbers to the characters, where 1 represents the first character. It is preferable to select a ranged character (such as Asta or March 7th) for the first position to facilitate initial encounters. The second line contains calibration data and should not be modified.

The third line indicates the difficulty level of the universe. If you want to play on difficulty level 1, change the value to 1 and save the file. The fourth line represents the path selection, with "巡猎" (The hunt) set as the default. You can directly modify it to another path, but keep in mind that the hunt path has been specifically optimized, so it is recommended not to change it unless necessary.

The fifth line represents the version of the map data and should not be altered.

By default, the program will enter the universe corresponding to the default settings. If the default universe is not the 6th world, remember to manually switch to the 6th world first!

**Update Files**

Double-click on `update.bat`.

### GUI Usage

**First-time Setup**

Enter the game and teleport your character to Herta's office. Then click on "Calibration" and wait for the camera angle to switch or for the character to finish spinning in place. A calibration success message will pop up.

If you change your mouse DPI or the game resolution/screen resolution/window scaling factor, you need to recalibrate!

In the settings, choose the desired difficulty and path. For team composition, use four numbers separated by three spaces, where 1 represents the first character (see the figure below for the numbering scheme). It is recommended to select a ranged character (Aisita or San Yue Qi) for the first position to facilitate initial encounters.

![Team Numbering](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

For example, if you want to select Natasha, Jing Yuan, Seele, and Yan Qing, input the following numbers for the team composition: 6 4 3 2

**Running the Automation**

Move your character close to the simulated universe (when the "F" key interaction prompt appears).

Click on "Run."

Note: After starting the automation or calibration process, do not move the game window. If you need to move it, please stop the automation first.

**TIPS:**

Press F8 or the "Stop" button to stop the automation.

The visibility setting controls whether the command-line window is displayed or hidden. By default, it is hidden.

Debug mode: Check (√) means that the program will not exit after getting lost, while "—" means that in addition to (√), the program will pause if it encounters a map with low similarity.

If you do not want the program to exit after getting lost, change the debug mode to (√).

Speedrun mode: Check (√) means that only the last enemy on each floor will be fought, while "—" means that in addition to (√), the program will enable sprinting.

The "Update Map" button is located in the lower-left corner (it only updates the map, not the core program).

Refer to the following instructions for recording maps.

Recommended minimum graphics settings:

![Graphics Settings](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/image_quality.jpg)

### Notification Plugin Usage (notif.exe)

If you are not using local multiple users, simply double-click on `notif.exe` to enable Windows notifications. You will receive notifications after each completion.

If you are using local multiple users, run the GUI in

 the child user account and run `notif.exe` in the main user account. This way, the notifications will be received in the main user account.

The counter will be automatically reset every week. If you want to manually change the counter, open `logs/notif.txt` and modify the information on the first line.

The notification plugin will display a tray icon in the lower-right corner.

----------------------------------------------------------------------------------------------

### Logic Overview

The logic for selecting blessings is fixed to "巡猎" (the hunt). Events are generally skipped, and the final floor's blessings are not strengthened. The curio are randomly chosen.

The pathfinding module is based on the mini-map.

The mini-map only recognizes white edge lines and yellow interaction points.

----------------------------------------------------------------------------------------------

Support for recording maps is available. The specific method is as follows:

Run `python states.py --debug=2 --find=1` (GUI version: set debug mode to "-", then click "Run").

If a new map is encountered and the character stops, end the automation and leave the simulated universe in the game.

Then run `python states.py --debug=2 --find=0` (GUI version: set debug mode to "-", then click "Record").

The program will automatically enter the map. During this process, do not move the mouse or press any keys.

After a few seconds, the character will retreat and then move forward. While the character is moving forward, you can move the mouse to change the camera angle or use the WASD keys.

Circle around the map until you feel it is sufficient. Then press F8 or Ctrl+C to end the process and obtain the map data. The data will be saved in the directory `imgs/maps/my_xxxxx` (sorted by modification time).

For maps with enemies, it is recommended to use Xi Er's combat skills. Being locked on can affect the recognition of the mini-map.

In the directory `imgs/maps/my_xxxxx`, there will be a file named `target.jpg`. You can use the built-in Paint application in Windows to open it and mark points on the map (you can refer to the `target.jpg` file in other map files).

Indigo: Path points, Yellow: End point, Green: Interaction point (question mark), Red: Enemy point

After recording, you can leave the simulated universe and run the automation again to test the map. If the test is successful, you have successfully recorded a new map!

----------------------------------------------------------------------------------------------

Welcome to join us and provide feedback on bugs. QQ Group: 831830526

----------------------------------------------------------------------------------------------

If you like this project, you can show your support by buying the author a cup of coffee!

![Support](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/money.jpg)
