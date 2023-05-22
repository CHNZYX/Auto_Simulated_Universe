@echo off
setlocal
git stash push -- info.txt
git pull
git stash apply
endlocal
pause