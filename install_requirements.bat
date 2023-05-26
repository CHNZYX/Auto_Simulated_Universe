%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
cd/d "%~dp0"
pip install -r requirements.txt -i https://pypi.doubanio.com/simple/
pause
