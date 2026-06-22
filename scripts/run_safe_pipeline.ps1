Write-Host "Zipping 7B Model..."
tar.exe -a -c -f Qwen2.5-VL-7B-Instruct.zip -C models Qwen2.5-VL-7B-Instruct

Write-Host "Downloading 32B Model safely..."
python scripts\prepare_offline_models.py

Write-Host "Zipping 32B Model..."
tar.exe -a -c -f Qwen2.5-VL-32B-Instruct-AWQ.zip -C models Qwen2.5-VL-32B-Instruct-AWQ

Write-Host "DONE!"
