@echo off
setlocal
git stash
git pull
git stash apply
endlocal
pause