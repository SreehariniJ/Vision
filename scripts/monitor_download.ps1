while ($true) {
    Clear-Host
    $sizeBytes = (Get-ChildItem -Path "c:\Users\Sreeharini\vision\models" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($null -ne $sizeBytes) {
        $sizeGB = [math]::Round($sizeBytes / 1GB, 2)
    } else {
        $sizeGB = 0
    }
    
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       LIVE MODEL DOWNLOAD MONITOR" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Currently downloading to: c:\Users\Sreeharini\vision\models"
    Write-Host ""
    Write-Host "Downloaded: " -NoNewline
    Write-Host "$sizeGB GB " -ForegroundColor Green -NoNewline
    Write-Host "out of ~39 GB total"
    Write-Host ""
    Write-Host "(Updates every 2 seconds. Close this window to stop monitoring.)"
    
    # Check zip files progress
    Write-Host ""
    Write-Host "--- COMPRESSION PROGRESS ---" -ForegroundColor Magenta
    
    $zip7bPath = "c:\Users\Sreeharini\vision\Qwen2.5-VL-7B-Instruct.zip"
    if (Test-Path $zip7bPath) {
        $zip7bSize = (Get-Item $zip7bPath).Length
        $zip7bGB = [math]::Round($zip7bSize / 1GB, 2)
        Write-Host "7B Model Zip: " -NoNewline
        Write-Host "$zip7bGB GB " -ForegroundColor Green -NoNewline
        Write-Host "compressed so far"
    } else {
        Write-Host "7B Model Zip: Waiting to start..." -ForegroundColor DarkGray
    }
    
    $zip32bPath = "c:\Users\Sreeharini\vision\Qwen2.5-VL-32B-Instruct-AWQ.zip"
    if (Test-Path $zip32bPath) {
        $zip32bSize = (Get-Item $zip32bPath).Length
        $zip32bGB = [math]::Round($zip32bSize / 1GB, 2)
        Write-Host "32B Model Zip: " -NoNewline
        Write-Host "$zip32bGB GB " -ForegroundColor Green -NoNewline
        Write-Host "compressed so far"
    } else {
        Write-Host "32B Model Zip: Waiting to start..." -ForegroundColor DarkGray
    }
    
    Start-Sleep -Seconds 2
}
