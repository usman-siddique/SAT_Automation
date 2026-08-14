@echo off
setlocal

set "RESULTS_DIR=reports\allure-results"
set "REPORT_DIR=reports\allure-report"
set "GENERATE_LOG=reports\allure-generate.log"

if not exist "%RESULTS_DIR%" (
    echo ERROR: No Allure results were found. Run pytest first.
    exit /b 1
)

where allure >nul 2>&1
if errorlevel 1 (
    echo ERROR: Allure Commandline is not installed.
    echo Run setup_allure.bat once on this laptop.
    exit /b 1
)

if exist "%REPORT_DIR%\history" (
    if not exist "%RESULTS_DIR%\history" mkdir "%RESULTS_DIR%\history"
    xcopy "%REPORT_DIR%\history\*" "%RESULTS_DIR%\history\" /E /I /Y >nul
)

echo Generating Allure report...
call allure generate "%RESULTS_DIR%" --clean -o "%REPORT_DIR%" >"%GENERATE_LOG%" 2>&1
if errorlevel 1 (
    type "%GENERATE_LOG%"
    exit /b 1
)
del /q "%GENERATE_LOG%" >nul 2>&1

echo Allure report generated at %REPORT_DIR%
echo.
set /p OPEN_REPORT="Open the Allure report now? (y/n): "
if /i "%OPEN_REPORT%"=="y" (
    echo Press Ctrl+C when you want to stop the Allure report server.
    call allure open "%REPORT_DIR%"
)

exit /b 0
