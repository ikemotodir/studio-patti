@echo off
setlocal
chcp 932 >nul
title STUDIO PATTI - apply layout
cd /d "%~dp0"
echo.
echo  ==========================================
echo   STUDIO PATTI  haichi wo hanei shimasu
echo  ==========================================
echo.
python apply_layout.py layout.json
if errorlevel 1 goto err
echo.
echo  koukai shite imasu ...
git add -A
git commit -q -m "haichi tool kara haichi wo hanei"
git pull --rebase -q
git push -q
if errorlevel 1 goto err
echo.
echo  OK!  1-2 fun de site ga kawarimasu.
echo.
pause
exit /b 0
:err
echo.
echo  shippai shimashita. gamen wo sono mama nokoshite kudasai.
echo.
pause
exit /b 1