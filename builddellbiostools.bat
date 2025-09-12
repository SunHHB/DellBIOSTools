@echo off
setlocal EnableExtensions

rem --- Refuse to run from System32 or as Admin (causes PyInstaller error) ---
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

echo [*] Ensuring PyInstaller is available...
python -m pip install --upgrade pip pyinstaller || (
  echo [!] pip/pyinstaller step failed.
  pause & exit /b 1
)

echo [*] Building...
python -m PyInstaller -F -w --clean --noconfirm ^
  -n "%APP_NAME%" ^
  --distpath "." ^
  --workpath "%WORK%" ^
  --specpath "%SPEC%" ^
  %ICONARG% ^
  "%ENTRY%"
if errorlevel 1 (
  echo [!] Build failed.
  pause & exit /b 1
)

echo [*] Cleaning temp...
rmdir /s /q "__pyi_tmp" >nul 2>&1

rem --- Report final EXE (no timestamp rename) ---
if exist "%APP_NAME%.exe" (
  echo [OK] Final EXE: %CD%\%APP_NAME%.exe
) else (
  echo [!] Build finished but EXE not found.
)

echo.
pause
