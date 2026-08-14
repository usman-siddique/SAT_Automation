@echo off
setlocal

echo ========================================
echo SAT Automation - Allure Setup
echo ========================================

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Python virtual environment was not found.
    echo Create it first with: python -m venv venv
    exit /b 1
)

echo Installing Python test dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java 8 or newer is required by Allure Report.
    exit /b 1
)

where allure >nul 2>&1
if not errorlevel 1 goto verify

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm was not found. Install Node.js or install Allure manually.
    exit /b 1
)

echo Installing Allure Commandline 2.43.0...
call npm install --global allure-commandline@2.43.0
if errorlevel 1 exit /b 1

:verify
echo.
echo Installed Allure version:
call allure --version
if errorlevel 1 exit /b 1

echo.
echo Allure setup completed successfully.
exit /b 0
