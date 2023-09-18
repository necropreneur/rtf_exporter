@echo off
SETLOCAL

REM Set script directory as current directory
cd /d %~dp0

REM Install virtualenv and create a venv
echo Installing virtualenv and creating venv...
pip install virtualenv
virtualenv venv

REM Activate the virtual environment
CALL venv\Scripts\activate

REM If requirements.txt file exists, then install requirements
IF EXIST requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Deactivate the virtual environment
CALL deactivate

ENDLOCAL