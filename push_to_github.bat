@echo off
echo ========================================
echo   Push to GitHub
echo ========================================
echo.

git init
git branch -m main

git add -A
git commit -m "Initial commit: Windows 11 Software Update Tool"

git remote add origin https://github.com/htani0817/Windows11-Software-Update-Tool.git

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo   Done!
echo   https://github.com/htani0817/Windows11-Software-Update-Tool
echo ========================================
pause