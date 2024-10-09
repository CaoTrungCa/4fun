@echo off
color 0F
mode con: cols=75 lines=20
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
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
)

:: Set Python download URL and installation path
set "pythonInstaller=python-3.10.0-amd64.exe"
set "downloadURL=https://www.python.org/ftp/python/3.10.0/%pythonInstaller%"
set "installPath=C:\Python310"

:: Download Python installer
echo Downloading Python installer...
bitsadmin /transfer "DownloadPython" /priority high %downloadURL% %pythonInstaller%

:: Run the installer
echo Installing Python...
start /wait %pythonInstaller% /quiet InstallAllUsers=1 PrependPath=1 TargetDir=%installPath%

:: Cleanup
del %pythonInstaller%

:: Verify installation
python --version
if %errorlevel% equ 0 (
    echo Python installed successfully.
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
) else (
    echo Python installation failed.
)

:end
endlocal
pause
