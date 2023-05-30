@echo off
if not exist ".\.git" (
    echo initializing Git...
    git init -b main
    git remote add origin https://github.com/CHNZYX/Auto_Simulated_Universe.git
    git fetch
)
git reset --hard HEAD
git pull
pause
