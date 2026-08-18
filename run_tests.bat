@echo off
setlocal enabledelayedexpansion
set PYTHONIOENCODING=utf-8

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
echo 5. Run Help tests
echo 6. Run User Used Car Buy Now tests (Paygent + Bank + PayPal)
echo 7. Run User New Car Buy Now tests (Paygent + Bank + PayPal)
echo 8. Run all User Buy Now tests (Used Car + New Car, all payments)
echo 9. Run User Used Car Reservation (priced / no Ask)
echo 10. Run User Used Car Reservation (Ask / invoice pending)
echo 11. Run all User Used Car Reservation tests (priced + Ask)
echo 12. Choose multiple test groups to run
echo 13. Exit
echo.
set /p choice="Enter your choice (1-13): "

if "%choice%"=="1" goto all
if "%choice%"=="2" goto sell
if "%choice%"=="3" goto car_services
if "%choice%"=="4" goto about_us
if "%choice%"=="5" goto help
if "%choice%"=="6" goto used_car_buy_flow
if "%choice%"=="7" goto new_car_buy_flow
if "%choice%"=="8" goto all_user_buy_flow
if "%choice%"=="9" goto used_car_reservation
if "%choice%"=="10" goto used_car_ask_reservation
if "%choice%"=="11" goto all_used_car_reservations
if "%choice%"=="12" goto multiple_tests
if "%choice%"=="13" goto end

echo Invalid test selection. No tests were started.
goto end

:all
echo Running all tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest %PYTEST_ARGS% %PARALLEL%
goto report

:sell
echo Running Sell My Car tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/sell_my_car/ %PYTEST_ARGS% %PARALLEL%
goto report

:car_services
echo Running Car Services tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/car_services/ %PYTEST_ARGS% %PARALLEL%
goto report

:about_us
echo Running About Us tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/about_us/ %PYTEST_ARGS% %PARALLEL%
goto report

:help
echo Running Help tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/help/ %PYTEST_ARGS% %PARALLEL%
goto report

:used_car_buy_flow
echo Running User Used Car Buy Now tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/buy_flow/user/used_car/ %PYTEST_ARGS% --force-reruns 0
goto report

:new_car_buy_flow
echo Running User New Car Buy Now tests...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/buy_flow/user/new_car/ %PYTEST_ARGS% --force-reruns 0
goto report

:all_user_buy_flow
echo Running all User Buy Now tests (Used Car + New Car)...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/buy_flow/user/ %PYTEST_ARGS% --force-reruns 0
goto report

:used_car_reservation
echo Running User Used Car Reservation test (priced / no Ask)...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/reservation/user/used_car/test_priced_reservation.py %PYTEST_ARGS% --force-reruns 0
goto report

:used_car_ask_reservation
echo Running User Used Car Reservation test (Ask / invoice pending)...
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/reservation/user/used_car/test_ask_reservation.py %PYTEST_ARGS% --force-reruns 0
goto report

:all_used_car_reservations
echo Running all User Used Car Reservation tests (priced + Ask)...
echo These state-changing tests run sequentially for the shared User account.
echo Ensure the account has no unpaid reservation before running both flows.
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest tests/reservation/user/used_car/ %PYTEST_ARGS% --force-reruns 0
goto report

:multiple_tests
echo.
echo Enter menu choices separated by commas.
echo Example: 2,5,8
echo Overlapping groups will run only once.
set "MULTI_CHOICES="
set "MULTI_TARGETS="
set "MULTI_INVALID="
set "MULTI_ANY="
set "MULTI_STATE_CHANGING="
set "MULTI_RERUN_ARGS="
set "MULTI_ALL="
set "MULTI_SELL="
set "MULTI_CAR_SERVICES="
set "MULTI_ABOUT="
set "MULTI_HELP="
set "MULTI_USED_BUY="
set "MULTI_NEW_BUY="
set "MULTI_ALL_BUY="
set "MULTI_PRICED_RESERVATION="
set "MULTI_ASK_RESERVATION="
set "MULTI_ALL_RESERVATIONS="
set /p MULTI_CHOICES="Enter choices 1-11 (example 2,5,8): "

if not defined MULTI_CHOICES (
    echo No test choices were entered.
    goto end
)

call :parse_multi_choices "!MULTI_CHOICES!"

if defined MULTI_INVALID (
    echo Invalid multi-test choice(s^): !MULTI_INVALID!
    echo Enter only test-group choices 1 through 11.
    goto end
)

if not defined MULTI_ANY (
    echo No valid test choices were entered.
    goto end
)

if defined MULTI_ALL (
    set "MULTI_TARGETS=tests"
) else (
    if defined MULTI_SELL set "MULTI_TARGETS=!MULTI_TARGETS! tests/sell_my_car/"
    if defined MULTI_ABOUT set "MULTI_TARGETS=!MULTI_TARGETS! tests/about_us/"
    if defined MULTI_CAR_SERVICES set "MULTI_TARGETS=!MULTI_TARGETS! tests/car_services/"
    if defined MULTI_HELP set "MULTI_TARGETS=!MULTI_TARGETS! tests/help/"

    if defined MULTI_ALL_BUY (
        set "MULTI_TARGETS=!MULTI_TARGETS! tests/buy_flow/user/"
    ) else (
        if defined MULTI_USED_BUY set "MULTI_TARGETS=!MULTI_TARGETS! tests/buy_flow/user/used_car/"
        if defined MULTI_NEW_BUY set "MULTI_TARGETS=!MULTI_TARGETS! tests/buy_flow/user/new_car/"
    )

    if defined MULTI_ALL_RESERVATIONS (
        set "MULTI_TARGETS=!MULTI_TARGETS! tests/reservation/user/used_car/"
    ) else (
        if defined MULTI_PRICED_RESERVATION set "MULTI_TARGETS=!MULTI_TARGETS! tests/reservation/user/used_car/test_priced_reservation.py"
        if defined MULTI_ASK_RESERVATION set "MULTI_TARGETS=!MULTI_TARGETS! tests/reservation/user/used_car/test_ask_reservation.py"
    )
)

set "MULTI_PARALLEL=!PARALLEL!"
if defined MULTI_STATE_CHANGING (
    set "MULTI_PARALLEL="
    set "MULTI_RERUN_ARGS=--force-reruns 0"
    echo State-changing tests selected. Parallel execution and reruns are disabled.
)

echo Running selected targets: !MULTI_TARGETS!
set HEADLESS=%HEADLESS%
set BROWSER=%BROWSER%
venv\Scripts\pytest !MULTI_TARGETS! %PYTEST_ARGS% !MULTI_PARALLEL! !MULTI_RERUN_ARGS!
goto report

:report
set "TEST_EXIT_CODE=%ERRORLEVEL%"
echo.
call generate_allure_report.bat
goto end

:end
echo.
echo Done!
pause
if defined TEST_EXIT_CODE exit /b %TEST_EXIT_CODE%
exit /b 0

:parse_multi_choices
set "MULTI_REMAINING=%~1"
:parse_multi_choice_next
if not defined MULTI_REMAINING goto :eof
for /f "tokens=1,* delims=," %%A in ("!MULTI_REMAINING!") do (
    set "MULTI_CURRENT=%%A"
    set "MULTI_REMAINING=%%B"
)
call :add_multi_choice "!MULTI_CURRENT!"
goto parse_multi_choice_next

:add_multi_choice
set "MULTI_ITEM=%~1"
set "MULTI_ITEM=!MULTI_ITEM: =!"
if not defined MULTI_ITEM goto :eof
if "!MULTI_ITEM!"=="1" (
    set "MULTI_ALL=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="2" (
    set "MULTI_SELL=1"
    set "MULTI_ANY=1"
    goto :eof
)
if "!MULTI_ITEM!"=="3" (
    set "MULTI_CAR_SERVICES=1"
    set "MULTI_ANY=1"
    goto :eof
)
if "!MULTI_ITEM!"=="4" (
    set "MULTI_ABOUT=1"
    set "MULTI_ANY=1"
    goto :eof
)
if "!MULTI_ITEM!"=="5" (
    set "MULTI_HELP=1"
    set "MULTI_ANY=1"
    goto :eof
)
if "!MULTI_ITEM!"=="6" (
    set "MULTI_USED_BUY=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="7" (
    set "MULTI_NEW_BUY=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="8" (
    set "MULTI_ALL_BUY=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="9" (
    set "MULTI_PRICED_RESERVATION=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="10" (
    set "MULTI_ASK_RESERVATION=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
if "!MULTI_ITEM!"=="11" (
    set "MULTI_ALL_RESERVATIONS=1"
    set "MULTI_ANY=1"
    set "MULTI_STATE_CHANGING=1"
    goto :eof
)
set "MULTI_INVALID=!MULTI_INVALID! !MULTI_ITEM!"
goto :eof
