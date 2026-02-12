@echo off
echo Setting up NL Compiler...
:: This adds the CURRENT folder to the User's PATH temporarily for this session
setx PATH "%PATH%;%cd%"
echo.
echo SUCCESS! 
echo 1. Please CLOSE this terminal and VS Code.
echo 2. Re-open VS Code.
echo 3. You can now just type 'nlc file.nl' anywhere!
pause