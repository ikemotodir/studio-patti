@echo off
setlocal
chcp 932 >nul
title STUDIO PATTI - apply layout
cd /d "C:\Users\studi\Desktop\PIXEL PATTI\Spooks\Patti_PIXEL\web"
echo.
echo  ==========================================
echo   STUDIO PATTI  haichi wo hanei shimasu
echo  ==========================================
echo.
python apply_layout.py
if errorlevel 1 goto err
echo.
echo  koukai shite imasu ...
git add -A
git commit -q -m "haichi tool kara haichi wo hanei"
git pull --rebase -q
if errorlevel 1 goto err
git push -q
if errorlevel 1 goto err
echo.
echo  OK!  1-2 fun de honban ni dete kimasu.
echo      http://studiopatti.jp/design.html
echo.
echo  modoshitai toki ha  [ haichi wo modosu.bat ]  wo double click.
echo.
pause
exit /b 0
:err
echo.
echo  *** shippai shimashita. kono gamen wo Claude ni misete kudasai. ***
echo.
pause
exit /b 1
