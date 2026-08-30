@echo off
echo Stopping all National University AI Assistant services...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM NU_AI_Server_Manager.exe 2>nul
echo.
echo All Python AI Chatbot services have been stopped.
pause
