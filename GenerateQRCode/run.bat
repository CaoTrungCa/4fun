@echo off
color 0F
mode con: cols=75 lines=20
echo Installing Python packages...
pip install -r Code/requirements.txt
echo Python packages installed successfully.

:run_script
echo Running Python script...
python Code/main.py
echo Python script execution completed.

choice /c YN /n /m "Do you want to run the script again? (Y/N): "

if errorlevel 2 exit
if errorlevel 1 goto run_script
