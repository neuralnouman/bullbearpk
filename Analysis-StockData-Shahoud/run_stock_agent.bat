@echo off
echo [INFO] Starting Stock Agent...

REM Step 1: Check if venv exists
IF NOT EXIST "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Step 2: Activate venv
call venv\Scripts\activate.bat

REM Step 3: Install dependencies
echo [INFO] Installing Python dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt

REM Step 4: Run the main application
echo [INFO] Running stock_agent.py...
python stock_agent.py

REM Keep the terminal open
echo.
pause
