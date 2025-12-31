@echo off
REM ============================================
REM Traverse Calculator - Windows Installer Build Script
REM ============================================
REM 
REM PREREQUISITES:
REM 1. Python 3.8+ installed (https://python.org)
REM 2. PyInstaller installed: pip install pyinstaller
REM 3. Inno Setup installed (https://jrsoftware.org/isinfo.php)
REM
REM Run this script from the project directory on Windows.
REM ============================================

echo.
echo ============================================
echo  Traverse Calculator - Build Script
echo ============================================
echo.

REM Step 1: Check for Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
python --version

REM Step 2: Install PyInstaller if not present
echo.
echo [2/4] Checking/Installing PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)
echo PyInstaller is ready.

REM Step 3: Build executable with PyInstaller
echo.
echo [3/4] Building executable with PyInstaller...
echo This may take a few minutes...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build using the spec file
pyinstaller TraverseCalculator.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo Executable built successfully!
echo Location: dist\TraverseCalculator.exe

REM Step 4: Create installer with Inno Setup
echo.
echo [4/4] Creating installer with Inno Setup...

REM Try common Inno Setup installation paths
set ISCC=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if %ISCC%=="" (
    echo.
    echo WARNING: Inno Setup not found in default locations.
    echo Please install it from: https://jrsoftware.org/isinfo.php
    echo.
    echo After installing, you can manually compile the installer by:
    echo   1. Open Inno Setup Compiler
    echo   2. Open installer.iss
    echo   3. Click Build ^> Compile
    echo.
    echo The standalone executable is still available at: dist\TraverseCalculator.exe
    pause
    exit /b 0
)

%ISCC% installer.iss

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  BUILD COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo Files created:
echo   - Executable: dist\TraverseCalculator.exe
echo   - Installer:  installer_output\TraverseCalculator_Setup.exe
echo.
echo You can distribute the installer file to users.
echo They will be able to install and run the application
echo without needing Python installed.
echo.
pause
