Write-Output "downloading..."

(New-Object System.Net.WebClient).DownloadFile('https://ghproxy.com/https://github.com/CHNZYX/Auto_Simulated_Universe/archive/main.zip', '.\repository.zip')
Expand-Archive -Path '.\repository.zip' -DestinationPath '../' -Force

Remove-Item ".\repository.zip"
Write-Output update finished
pause