@echo off
color 0F
mode con: cols=75 lines=20
echo Installing Python packages...
pip install -r Code/requirements.txt
echo Python packages installed successfully.

:choose_script
echo.
echo Select the script to run:
echo 1. One
echo 2. All
choice /c 12 /n /m "Enter your choice (1 for One, 2 for All): "

if errorlevel 2 goto run_all
if errorlevel 1 goto run_main

:run_main
echo Running Python main.py...
python Code/main.py
echo Python script main.py execution completed.
goto ask_again

:run_all
echo Running Python all.py...
python Code/all.py
echo Python script all.py execution completed.

:ask_again
choice /c YN /n /m "Do you want to choose a script and run it again? (Y/N): "
if errorlevel 2 exit
if errorlevel 1 goto choose_script
