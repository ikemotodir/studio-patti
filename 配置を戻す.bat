@echo off
setlocal
chcp 932 >nul
title STUDIO PATTI - undo layout
cd /d "C:\Users\studi\Desktop\PIXEL PATTI\Spooks\Patti_PIXEL\web"
echo.
echo   hitotsu mae no haichi ni modoshimasu.
echo.
git pull --rebase -q
git revert --no-edit HEAD
if errorlevel 1 goto err
git push -q
if errorlevel 1 goto err
echo.
echo  OK!  modorimashita.
echo.
pause
exit /b 0
:err
echo.
echo  *** shippai shimashita. kono gamen wo Claude ni misete kudasai. ***
echo.
pause
exit /b 1
