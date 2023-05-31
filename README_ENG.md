# Auto_Simulated_Universe
StarSky Railway - Auto Simulation Universe Automation

There is a breakpoint resumption function, so you can switch to do other things and come back to continue the automation.

Currently, only Simulation Universe 4 and 6 are supported, and the map data is mostly recorded.

----------------------------------------------------------------------------------------------

## Disclaimer
This software is an external tool designed to automate gameplay in the game Honkai Impact 3rd. It is designed to interact with the game solely through the existing user interface and comply with relevant laws and regulations. The purpose of this software package is to provide simplification and user interaction with the game through functionality, and it is not intended to disrupt game balance or provide any unfair advantages. This software package does not modify any game files or game code in any way.

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

Please note that according to MiHoYo's [Fair Gaming Declaration for Honkai Impact 3rd: Star Sky Railway]([https://hsr.hoyoverse.com/en-us/news/111244](https://sr.mihoyo.com/news/111246?nav=news&type=notice)):

    "The use of cheating software, accelerators, scripts, or other third-party tools that disrupt the fairness of the game is strictly prohibited."
    "Once discovered, miHoYo (hereinafter referred to as 'we') will take measures such as deducting illegal gains, freezing game accounts, and permanently banning game accounts depending on the severity and frequency of violations."

### Usage

Only supports 1920\*1080 (windowed or fullscreen), enable detailed blessing description, and select Simplified Chinese as the text language.

Default universe: For example, if your current simulated universe is set to default to Universe 4 but you want to automate Universe 6, please enter Universe 6 first to change the default universe.

If you haven't had much experience with Python, it is recommended to directly download the GUI version from the release and read the GUI usage instructions.

**First-time Setup**

Double-click on install_requirements.bat to install the required libraries.

Enter the game and teleport your character to the office in Black Tower, then double-click on **align.bat**, switch back to the game interface, and wait for the camera angle adjustment/spinning to finish.

If **align.bat** crashes, you can try running it as an administrator:
```
python align_angle.py
```

If you have changed the mouse DPI or game resolution/screen resolution/window scaling ratio, you need to recalibrate!

**Running the Automation**

Approach the Simulated Universe (F key interaction prompt appears).

Double-click on run.bat or run with administrator privileges:
```
python states.py --find=1
```

The first line in info.txt saves the character selected at the start of the Simulated Universe. It is recommended to change it to your own team composition, where 1 represents the first character. It is better to select a ranged character (e.g., Asutera, Sangetsu) in the first position for easier monster engagement. The second line contains calibration data and should not be changed!

The third line is the difficulty of the universe. If you want to play on difficulty level 1, change it to 1 and save. The fourth line is the choice of fate, defaulting to "Patrol."

 You can directly modify it to another fate, but patrol has been specially optimized, so avoid changing it unless necessary.

The fifth line is the version of the map data and is not recommended to be changed.

You will automatically enter the corresponding universe based on the default! If your default is not Universe 6, remember to manually switch to Universe 6 first!

Attention!!! Do not move the game window after starting the automation/calibration! If you need to move it, please stop the automation first!

**Updating Files**

Double-click on update.bat.

### GUI Usage Instructions

**First-time Setup**

Enter the game and teleport your character to the office in Black Tower, then click on "Calibrate" and wait for the camera angle adjustment/spinning to finish. A calibration success message will pop up.

If you have changed the mouse DPI or game resolution/screen resolution/window scaling ratio, you need to recalibrate!

In the settings, select the desired difficulty and fate. For the team composition, separate the four numbers with three spaces, with 1 representing the first character (see the team numbering guide in the image below). It is better to select a ranged character (e.g., Asutera, Sangetsu) in the first position for easier monster engagement.

![Team Numbering Guide](https://github.com/CHNZYX/Auto_Simulated_Universe/blob/main/imgs/team.jpg)

**Running the Automation**

Approach the Simulated Universe (F key interaction prompt appears).

Click on "Run".

**TIPS:**

Press F8 or the "Stop" button to stop the automation.

"Visibility" indicates whether to show/hide the command line window. It is hidden by default.

"Debug Mode": √ means that the automation will not stop after getting lost, — means it will pause when encountering a map with low similarity based on √.

If you don't want the automation to stop after getting lost, change the debug mode to √.

The bottom-left corner has an "Update Map" button (only updates the map, not the core program).

Refer to the following text for map recording.

----------------------------------------------------------------------------------------------

### Some Logic

The logic for selecting blessings is fixed on "Patrol," and most events are skipped. The final layer will not enhance blessings, and relics are randomly selected.

The pathfinding module is based on the mini-map, so when running, the character will lower its head to keep the mini-map from being affected by the highlighted sky.

Only white edge lines and yellow interaction points will be recognized in the mini-map.

----------------------------------------------------------------------------------------------

Supports map recording, the specific method is as follows:

Run `python states.py --debug=2 --find=1` (GUI version: set debug mode to -, then click "Run").

If a new map is encountered, the character will stop. At this point, end the automation and exit the Simulated Universe in the game.

Then run `python states.py --debug=2 --find=0` (GUI version: set debug mode to -, then click "Record").

The program will automatically enter the map. During this process, do not move the mouse or press any keys on the keyboard.

After a few seconds, the character will move backward and then forward. While the character is moving forward, you can move the mouse to change the camera angle or use the WASD keys on the keyboard.

Circle around in the map and when it feels sufficient, press F8 or ctrl+c to terminate the process. This will provide the map data, which will be saved in the directory `imgs/maps/my_xxxxx` (you can sort by modification time).

For maps with monsters, it is best to use Herrscher's ultimate skill, as being locked onto will affect the mini-map recognition.

In the

 directory `imgs/maps/my_xxxxx`, there will be a `target.jpg` file. You can open it using the built-in Paint program in Windows and mark points on it (you can refer to the `target.jpg` file in other map files).

Indigo: Path point, Yellow: Endpoint, Green: Interaction point (question mark), Red: Monster point.

After finishing the recording, you can exit and run the automation again to test the map. If it passes the test, you have successfully recorded a new map!

----------------------------------------------------------------------------------------------

Welcome to join and provide feedback on bugs. QQ Group: 831830526
