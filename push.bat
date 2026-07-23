@echo off
title Push to GitHub
color 0A

echo.
echo  ================================================
echo   Pushing to GitHub...
echo  ================================================
echo.

:: Init repo if not already
if not exist ".git" (
    echo  [*] Initializing git repo...
    git init
    git branch -M main
)

:: Set remote
git remote remove origin 2>nul
git remote add origin https://github.com/rowanchanner/tiktok-automation-tool.git

:: Stage, commit, push
git add -A
git commit -m "Initial commit — TikTok Automation Suite"
git push -u origin main

echo.
echo  [*] Done. Check https://github.com/rowanchanner/tiktok-automation-tool
echo.
pause
