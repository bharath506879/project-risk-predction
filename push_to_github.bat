@echo off
cd /d "c:\projrct risk predction"
python push_to_github.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Files successfully pushed to GitHub!
    echo 📍 Repository: https://github.com/bharath506879/project-risk-predction
) else (
    echo.
    echo ❌ Failed to push files
)
pause
