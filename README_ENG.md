# Auto_Simulated_Universe
Honkai Star Rail - Automated Simulation Universe

It has a certain breakpoint recovery function, so you can switch to do other things and switch back to continue automation.

Currently, only Simulated Universe 6 is supported, and the map data has been basically recorded.

----------------------------------------------------------------------------------------------

## Disclaimer
This software is an external tool designed to automate gameplay in the game Honkai Impact 3rd. It is designed to interact with the game only through the existing user interface and comply with relevant laws and regulations. The purpose of this software package is to provide simplification and functionality for users to interact with the game, and it is not intended to disrupt game balance in any way or provide any unfair advantage. This software package does not modify any game files or game code in any way.

This software is open source, free of charge, and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

Please note that according to MiHoYo's [Fair Play Declaration for Honkai Impact 3rd](https://hsr.hoyoverse.com/en-us/news/111244):

    "The use of cheats, accelerators, scripts or other third-party tools that disrupt the fairness of the game is strictly prohibited."
    "Once discovered, miHoYo (hereinafter referred to as 'we') will take measures such as deducting illicit gains, freezing game accounts, and permanently banning game accounts, depending on the severity and frequency of the violations."

### Usage

**First run**

Double click on `install_requirements.bat` to install the required libraries.

Enter the game and teleport your character to the office in the Black Tower. Then double click on **`align.bat`**, switch back to the game interface, and wait for the camera angle transition or spinning to finish.

If **`align.bat`** crashes, you can try running the following command as administrator:
```python align_angle.py```

If you change the mouse DPI or the game resolution/screen resolution/window scaling ratio, you need to recalibrate!

**Running the automation**

Bring your character close to the Simulated Universe (the "F" key interaction prompt appears).

Double click on `run.bat` or run the following command with administrator privileges:
```python states.py --find=1```

Only supports 1920*1080 (windowed or fullscreen), with detailed blessing descriptions enabled and text language set to Simplified Chinese.

The first line in `info.txt` saves the character selected at the start of the Simulated Universe. It is recommended to change it to your own team composition, with 1 indicating the first character. It is best to select a ranged character (such as Seele Vollerei or Mei Raiden) in the first slot for easier monster encounters. The second line contains calibration data and should not be modified!

The third line is the difficulty level of the universe. If you want to play on difficulty level 1, change it to 1 and save. The fourth line is the fate option, with "巡猎" (patrol) being the default. You can directly modify it to other options, but patrol has been optimized, so only change it if necessary.

The fifth line is the version of the map data, and it is not recommended to change it.

The default is to enter the universe you default to! If your default is not the 6th universe, remember to manually

 switch to the 6th universe first!

Note!!!! After starting the run/calibration, do not move the game window! If you need to move it, please stop the automation first!

**Updating files**

Double click on `update.bat`

**GUI usage**

Press F8 to stop the run, and click the button in the lower right corner to update the map.

Visibility indicates whether the command line window is displayed or hidden by default.

Debug mode: √ means no settlement after getting lost, — means pausing when encountering maps with low similarity based on √.

----------------------------------------------------------------------------------------------

### Partial Logic

The logic for selecting blessings is to always choose patrol, skipping most events. The last level will not strengthen the blessing, and the oddities are selected randomly.

The pathfinding module is based on the minimap, so when running, the character will look down to keep the minimap from being affected by the highlighted sky.

Only white edge lines and yellow interaction points are recognized on the minimap.

----------------------------------------------------------------------------------------------

Support for adding maps, the specific method is:

Run `python states.py --debug=2 --find=1`

If a new map is encountered, the character will stop, at this point, end the automation and leave the Simulated Universe in the game.

Then run `python states.py --debug=2 --find=0`

Note that the initial state must be when you just enter the map and the camera angle has not changed.

After a few seconds, the character will move back and then move forward. While the character is moving forward, you can move the mouse to change the camera angle.

Go around the map and when it feels about right, press Ctrl+C to end the process. You will get the map data. It will be saved in the directory `imgs/maps/xxxxx` (sorted by modification time).

It is best to keep looking down to reduce interference from the highlighted sky.

For maps with enemies, it is best to use Seele's Ultimate Skill, as being locked onto will affect the recognition on the minimap.

The light blue fan shape (spotlight) on the minimap that represents the character's field of view will also affect the recognition of the white edge lines on the minimap. Therefore, try to minimize the spotlight's coverage of the white edges.

There will be a `target.jpg` file in the `imgs/maps/xxxxx` directory. You can open it with the built-in Paint program in Windows and mark points on it (you can refer to other target.jpg files in other map directories).

Indigo: path point Yellow: destination Green: interaction point (question mark) Red: enemy point

----------------------------------------------------------------------------------------------

Welcome to join, welcome to give feedback on bugs, QQ group: 831830526
