@echo off
set PYTHON="C:\Users\ZYREX\AppData\Local\Programs\Python\Python311\python.exe"
if not exist %PYTHON% (
    set PYTHON=python
)
echo ========================================================
echo   Launching Mini-SIEM Interactive Attack Simulator...
echo ========================================================
%PYTHON% simulator.py %*
pause
