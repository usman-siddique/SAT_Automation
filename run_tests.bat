@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SAT Automation Test Runner
echo ========================================
echo.
echo Select test environment:
echo 1. Sprint - https://sprint.shineauto.info/ (default)
echo 2. Development - https://development.satjapan.info/
echo.
set /p environment_choice="Enter choice (1 or 2): "

if "%environment_choice%"=="2" (
    set "BASE_URL=https://development.satjapan.info"
    echo Running against DEVELOPMENT
) else (
    set "BASE_URL=https://sprint.shineauto.info"
    echo Running against SPRINT
)

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
echo Select browser:
echo 1. Chromium (default)
echo 2. Firefox
echo.
set /p browser_choice="Enter choice (1 or 2): "

if "%browser_choice%"=="2" (
    set BROWSER=firefox
    echo Running with Firefox
) else (
    set BROWSER=chromium
    echo Running with Chromium
)

echo.
echo Run tests in parallel? (y/n)
set /p parallel="Enter choice: "
if /i "%parallel%"=="y" (
    set PARALLEL=-n auto
    echo Parallel execution enabled (using all CPU cores^)
) else (
    set PARALLEL=
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
echo 6. Run Warranty Service tests
echo 7. Run Finance Service tests
echo 8. Run Non Stolen Vehicle tests
echo 9. Run Buy Now / Order Placement tests
echo 10. Exit
echo.
set /p choice="Enter your choice (1-10): "

if "%choice%"=="1" goto all
if "%choice%"=="2" goto sell
if "%choice%"=="3" goto car_services
if "%choice%"=="4" goto about_us
if "%choice%"=="5" goto shipping
if "%choice%"=="6" goto warranty
if "%choice%"=="7" goto finance
if "%choice%"=="8" goto non_stolen
if "%choice%"=="9" goto buy_flow
if "%choice%"=="10" goto end

echo Invalid test selection. No tests were started.
goto end

:all
echo Running all tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest %PYTEST_ARGS% %PARALLEL%
goto end

:sell
echo Running Sell My Car tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/sell_my_car/ %PYTEST_ARGS% %PARALLEL%
goto end

:car_services
echo Running Car Services tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/ %PYTEST_ARGS% %PARALLEL%
goto end

:about_us
echo Running About Us tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/about_us/ %PYTEST_ARGS% %PARALLEL%
goto end

:shipping
echo Running Shipping Schedule tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/test_shipping_schedule.py %PYTEST_ARGS% %PARALLEL%
goto end

:warranty
echo Running Warranty Service tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/test_warranty_service.py %PYTEST_ARGS% %PARALLEL%
goto end

:finance
echo Running Finance Service tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/test_finance_service.py %PYTEST_ARGS% %PARALLEL%
goto end

:non_stolen
echo Running Non Stolen Vehicle tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/test_non_stolen_vehicle.py %PYTEST_ARGS% %PARALLEL%
goto end

:buy_flow
echo Running Buy Now / Order Placement tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/buy_flow/ %PYTEST_ARGS% %PARALLEL%
goto end

:end
echo.
echo Done!
pause
