@echo off
set PYTHON="C:\Users\ZYREX\AppData\Local\Programs\Python\Python311\python.exe"
if not exist %PYTHON% (
    set PYTHON=python
)
echo ========================================================
echo   Starting Mini-SIEM Command Center on port 8000...
echo   Dashboard URL: http://127.0.0.1:8000
echo   API Docs URL:  http://127.0.0.1:8000/docs
echo ========================================================
%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
