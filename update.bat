@echo off
if not exist ".\.git" (
    echo initializing Git...
    git init -b main
    git remote add origin https://github.com/CHNZYX/Auto_Simulated_Universe.git
    git fetch
)
setlocal
git stash push info.txt
git pull
git stash apply
endlocal
pause