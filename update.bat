@echo off
if not exist ".\.git" (
    echo initializing Git...
    git init -b main
    git commit --allow-empty -n -m "Initial commit"
    git remote add origin https://github.com/CHNZYX/Auto_Simulated_Universe.git
)
git fetch
git reset --hard HEAD
git pull origin main --allow-unrelated-histories
pause
