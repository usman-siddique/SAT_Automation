@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SAT Automation Test Runner
echo ========================================
echo.
echo Select browser mode:
echo 1. Headed (visible browser)
echo 2. Headless (invisible browser)
echo.
set /p mode="Enter choice (1 or 2): "

if "%mode%"=="1" (
    set HEADLESS=false
    set PYTEST_ARGS=-v
    echo Running in HEADED mode (verbose output, no prints^)
) else if "%mode%"=="2" (
    set HEADLESS=true
    set PYTEST_ARGS=-v
    echo Running in HEADLESS mode (verbose output, no prints^)
) else (
    echo Invalid choice. Defaulting to HEADED.
    set HEADLESS=false
    set PYTEST_ARGS=-v
)

echo.
echo ========================================
echo Test Selection Menu
echo ========================================
echo.
echo 1. Run all tests
echo 2. Run Sell My Car tests
echo 3. Run Car Services tests
echo 4. Run About Us tests
echo 5. Run Shipping Schedule tests
echo 6. Run Insurance Services tests
echo 7. Run Finance Service tests
echo 8. Run Non Stolen Vehicle tests
echo 9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto all
if "%choice%"=="2" goto sell
if "%choice%"=="3" goto car_services
if "%choice%"=="4" goto about_us
if "%choice%"=="5" goto shipping
if "%choice%"=="6" goto insurance
if "%choice%"=="7" goto finance
if "%choice%"=="8" goto non_stolen
if "%choice%"=="9" goto end

:all
echo Running all tests...
set HEADLESS=%HEADLESS%
pytest %PYTEST_ARGS%
goto end

:sell
echo Running Sell My Car tests...
set HEADLESS=%HEADLESS%
pytest tests/sell_my_car/ %PYTEST_ARGS%
goto end

:car_services
echo Running Car Services tests...
set HEADLESS=%HEADLESS%
pytest tests/car_services/ %PYTEST_ARGS%
goto end

:about_us
echo Running About Us tests...
set HEADLESS=%HEADLESS%
pytest tests/about_us/ %PYTEST_ARGS%
goto end

:shipping
echo Running Shipping Schedule tests...
set HEADLESS=%HEADLESS%
pytest tests/car_services/test_shipping_schedule.py %PYTEST_ARGS%
goto end

:insurance
echo Running Insurance Services tests...
set HEADLESS=%HEADLESS%
pytest tests/car_services/test_insurance_services.py %PYTEST_ARGS%
goto end

:finance
echo Running Finance Service tests...
set HEADLESS=%HEADLESS%
pytest tests/car_services/test_finance_service.py %PYTEST_ARGS%
goto end

:non_stolen
echo Running Non Stolen Vehicle tests...
set HEADLESS=%HEADLESS%
pytest tests/car_services/test_non_stolen_vehicle.py %PYTEST_ARGS%
goto end

:end
echo.
echo Done!
pause