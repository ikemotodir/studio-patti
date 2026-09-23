@echo off
setlocal
chcp 932 >nul
title STUDIO PATTI - undo layout
cd /d "%~dp0"
echo.
echo   hitotsu mae no haichi ni modoshimasu.
echo.
git pull --rebase -q
for /f "delims=" %%H in ('git log -1 --format^=%%H -- layout.json') do set LJ=%%H
git revert --no-edit HEAD
if errorlevel 1 goto err
git revert --no-edit %LJ%
if errorlevel 1 goto err
git push -q
if errorlevel 1 goto err
echo.
echo  OK!  modorimashita. (layout.json mo modoshimashita)
echo.
pause
exit /b 0
:err
echo.
echo  modosemasen deshita. gamen wo sono mama nokoshite kudasai.
echo.
pause
exit /b 1