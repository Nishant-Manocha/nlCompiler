$path = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($path -notlike "*$PSScriptRoot*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$path;$PSScriptRoot", "User")
    Write-Host "Setup Complete! Restart VS Code and you can now use 'nlc' anywhere." -ForegroundColor Green
} else {
    Write-Host "Already set up!" -ForegroundColor Yellow
}