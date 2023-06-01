@echo off

echo downloading...

powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://github.com/CHNZYX/Auto_Simulated_Universe/archive/main.zip', '.\repository.zip')"

powershell -Command "Expand-Archive -Path '.\repository.zip' -DestinationPath '../' -Force"

del ".\repository.zip"

echo update finished

pause
