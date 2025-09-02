@echo off
setlocal EnableDelayedExpansion

echo =====================================
echo   DellBIOSTools - Build EXE
echo =====================================
echo.

pushd %~dp0

:: ---------- 1) Check Python ----------
echo [*] Checking for Python...
where python
if errorlevel 1 (
  where py
  if errorlevel 1 (
    echo [!] Python not found.
    echo     Attempting to install Python...
  ) else (
    set "PYEXE=py"
  )
) else (
  set "PYEXE=python"
)

:: ---------- 2) Install via Winget ----------
if not defined PYEXE (
  echo [*] Trying Winget Python install...
  winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements
)

:: ---------- 3) If still missing, download installer ----------
if not defined PYEXE (
  where python && set "PYEXE=python"
  if not defined PYEXE where py && set "PYEXE=py"
)

if not defined PYEXE (
  echo [*] Downloading Python installer...
  set "PY_VER=3.12.5"
  set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"
  set "TMP_EXE=%TEMP%\\python-installer-%RANDOM%.exe"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%TMP_EXE%'"
  "%TMP_EXE%" /quiet PrependPath=1 Include_pip=1 Shortcuts=0
  timeout /t 8
  set "PYEXE=python"
)

echo [OK] Using Python launcher: %PYEXE%
echo.

:: ---------- 4) Install PyInstaller ----------
echo [*] Upgrading pip...
%PYEXE% -m pip install --upgrade pip

echo [*] Installing PyInstaller...
%PYEXE% -m pip install pyinstaller

:: ---------- 5) Build ----------
echo [*] Building exe with PyInstaller...
%PYEXE% -m PyInstaller --noconfirm --onefile --windowed DellBiosTools.py

if not exist "dist\\DellBiosTools.exe" (
  echo [!] Build failed!
  pause
  exit /b 1
)

:: ---------- 6) Move and Clean ----------
echo [*] Moving exe to project root...
copy /y "dist\\DellBiosTools.exe" ".\\DellBiosTools.exe"

echo [*] Cleaning up temporary files...
rmdir /s /q build
rmdir /s /q dist
del DellBiosTools.spec

echo.
echo ✅ Build complete! Your exe is ready:
echo    %cd%\\DellBiosTools.exe
echo.
pause
endlocal
