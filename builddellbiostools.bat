@echo off
setlocal EnableExtensions

rem --- Refuse to run from System32 or as Admin (causes PyInstaller issues) ---
if /I "%CD%"=="C:\Windows\System32" (
  echo [!] Don't run from C:\Windows\System32. Open this folder in Explorer, type CMD in the address bar, and run again.
  pause & exit /b 1
)
net session >nul 2>&1
if %ERRORLEVEL%==0 (
  echo [!] You're running as Administrator. Close this window and run as a normal user.
  pause & exit /b 1
)

echo =====================================
echo   DellBiosTools - Build EXE (local)
echo =====================================
echo [i] Working dir: %CD%
echo.

set "APP_NAME=DellBiosTools"
set "ENTRY=DellBiosTools.pyw"
set "ICONDIR=%CD%\icon"
set "ICONFILE=%ICONDIR%\DellBiosTools.ico"
set "WORK=__pyi_tmp\build"
set "SPEC=__pyi_tmp\spec"
set "PY_LOCAL_INSTALLER=%~dp0python-3.11.9-amd64.exe"

if not exist "%ENTRY%" (
  echo [!] %ENTRY% not found in this folder.
  pause & exit /b 1
)

rem --- ICON handling ---
set "ICONARG="
if exist "%ICONFILE%" (
  set "ICONARG=--icon ""%ICONFILE%"""
  echo [OK] Icon will be embedded: %ICONFILE%
) else (
  echo [i] No icon found in: %ICONFILE%
)

rem ---------------------------------------------------------------------------
rem Try to use an EXISTING Python 3.11 first
rem Order: py -3.11  -> python (check version) -> local installer
rem ---------------------------------------------------------------------------
set "USE_PYLAUNCHER="
set "RUNPY="
set "PYVER="

rem Try the Python launcher for 3.11
py -3.11 -V >nul 2>&1
if not errorlevel 1 (
  set "USE_PYLAUNCHER=1"
  echo [i] Found Python via launcher: py -3.11
) else (
  rem Try plain "python" and verify it's 3.11.x
  for /f "usebackq tokens=*" %%v in (`python -c "import sys; print(sys.version.split()[0])" 2^>NUL`) do set "PYVER=%%v"
  if defined PYVER (
    echo [i] python reports version: %PYVER%
    echo %PYVER%| findstr /b "3.11" >nul
    if not errorlevel 1 (
      set "RUNPY=python"
      echo [i] Using existing python on PATH.
    )
  )
)

rem If still nothing 3.11, install from local bundled installer
if not defined USE_PYLAUNCHER if not defined RUNPY (
  if not exist "%PY_LOCAL_INSTALLER%" (
    echo [!] Python 3.11 not found, and local installer missing:
    echo     %PY_LOCAL_INSTALLER%
    echo     Place python-3.11.9-amd64.exe next to this BAT and run again.
    pause & exit /b 1
  )
  echo [*] Installing Python 3.11.9 from local installer...
  start "" /wait "%PY_LOCAL_INSTALLER%" ^
    /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=1 Shortcuts=0 Include_test=0 SimpleInstall=1

  rem Probe common install locations and launcher
  set "CAND1=%LocalAppData%\Programs\Python\Python311\python.exe"
  set "CAND2=%ProgramFiles%\Python311\python.exe"
  set "CAND3=%ProgramFiles(x86)%\Python311\python.exe"

  if exist "%CAND1%" set "RUNPY=%CAND1%"
  if not defined RUNPY if exist "%CAND2%" set "RUNPY=%CAND2%"
  if not defined RUNPY if exist "%CAND3%" set "RUNPY=%CAND3%"

  rem If path not updated in this session, the launcher usually is available
  if not defined RUNPY (
    py -3.11 -V >nul 2>&1 && set "USE_PYLAUNCHER=1"
  )

  if not defined RUNPY if not defined USE_PYLAUNCHER (
    echo [!] Python 3.11 could not be located after installation.
    echo     Try closing this window and running the BAT again.
    pause & exit /b 1
  )
)

if defined RUNPY (
  echo [i] Using Python: "%RUNPY%"
) else (
  echo [i] Using Python launcher: py -3.11
)

rem ---------------------------------------------------------------------------
rem Ensure PyInstaller is available (in the chosen interpreter)
rem ---------------------------------------------------------------------------
echo [*] Ensuring PyInstaller is available...
if defined RUNPY (
  "%RUNPY%" -m pip install --upgrade pip pyinstaller
) else (
  py -3.11 -m pip install --upgrade pip pyinstaller
)
if errorlevel 1 (
  echo [!] pip/pyinstaller step failed.
  pause & exit /b 1
)

rem ---------------------------------------------------------------------------
rem Build EXE next to the .pyw, then clean temp
rem ---------------------------------------------------------------------------
echo [*] Building...
if defined RUNPY (
  "%RUNPY%" -m PyInstaller -F -w --clean --noconfirm ^
    -n "%APP_NAME%" ^
    --distpath "." ^
    --workpath "%WORK%" ^
    --specpath "%SPEC%" ^
    %ICONARG% ^
    "%ENTRY%"
) else (
  py -3.11 -m PyInstaller -F -w --clean --noconfirm ^
    -n "%APP_NAME%" ^
    --distpath "." ^
    --workpath "%WORK%" ^
    --specpath "%SPEC%" ^
    %ICONARG% ^
    "%ENTRY%"
)
if errorlevel 1 (
  echo [!] Build failed.
  pause & exit /b 1
)

echo [*] Cleaning temp...
rmdir /s /q "__pyi_tmp" >nul 2>&1

rem ---------------------------------------------------------------------------
rem Timestamped rename: DellBiosTools-YYYY-MM-DD_HHMM.exe
rem ---------------------------------------------------------------------------
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
  set mm=%%a
  set dd=%%b
  set yyyy=%%c
)
for /f "tokens=1-2 delims=:." %%h in ("%time%") do (
  set hh=%%h
  set nn=%%i
)
set hh=0%hh%
set hh=%hh:~-2%
set nn=0%nn%
set nn=%nn:~-2%
set "STAMP=%yyyy%-%mm%-%dd%_%hh%%nn%"
set "NEWEXE=%APP_NAME%-%STAMP%.exe"

if exist "%APP_NAME%.exe" (
  ren "%APP_NAME%.exe" "%NEWEXE%"
  echo [OK] Final EXE: %CD%\%NEWEXE%
) else (
  echo [!] Build finished but EXE not found.
)

echo.
pause
