function nlc_func {
    & "$PSScriptRoot\nlc.exe" $args
}
Set-Alias nlc nlc_func
Write-Host "NL Compiler activated! Use 'nlc' to run your commands." -ForegroundColor Green