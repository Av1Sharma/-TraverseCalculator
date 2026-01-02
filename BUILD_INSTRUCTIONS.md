# Traverse Calculator - Windows Installer Build Guide

This guide explains how to create a professional Windows installer for the Traverse Calculator application.

## Prerequisites

You will need the following installed on a **Windows** computer:

### 1. Python 3.8 or higher
- Download from: https://python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation

### 2. PyInstaller
- Open Command Prompt and run:
  ```cmd
  pip install pyinstaller
  ```

### 3. Inno Setup 6 (for creating the installer)
- Download from: https://jrsoftware.org/isinfo.php
- Install with default settings

## Quick Build (Automatic)

1. Copy all project files to your Windows computer
2. Double-click `build_installer.bat`
3. Wait for the build to complete
4. Find your installer at: `installer_output\TraverseCalculator_Setup.exe`

## Manual Build Steps

### Step 1: Build the Executable

Open Command Prompt in the project directory and run:

```cmd
pyinstaller TraverseCalculator.spec --noconfirm
```

This creates `dist\TraverseCalculator.exe` - a standalone executable that includes Python and all dependencies.

### Step 2: Test the Executable

Before creating the installer, test that the executable works:

```cmd
dist\TraverseCalculator.exe
```

### Step 3: Create the Installer

**Option A: Using Inno Setup GUI**
1. Open Inno Setup Compiler
2. File → Open → select `installer.iss`
3. Build → Compile (or press F9)

**Option B: Using Command Line**
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

The installer will be created at: `installer_output\TraverseCalculator_Setup.exe`

## Output Files

After building, you will have:

| File | Location | Description |
|------|----------|-------------|
| Standalone .exe | `dist\TraverseCalculator.exe` | Can be run directly without installation |
| Installer | `installer_output\TraverseCalculator_Setup.exe` | Professional installer with shortcuts |

## Customization

### Adding an Icon

1. Create or obtain a `.ico` file (256x256 recommended)
2. Name it `icon.ico` and place it in the project directory
3. Uncomment the `SetupIconFile=icon.ico` line in `installer.iss`
4. Rebuild

### Changing Publisher/Version

Edit the following lines in `installer.iss`:

```iss
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
```

## Distributing to Users

Give users the `TraverseCalculator_Setup.exe` file. When they run it:

1. A setup wizard will guide them through installation
2. The app will be installed to Program Files
3. Start Menu and Desktop shortcuts will be created (optional)
4. They can uninstall via Windows Settings → Apps

**No Python installation required for end users!**

## Troubleshooting

### "Python not found"
- Reinstall Python and check "Add Python to PATH"
- Restart Command Prompt after installation

### PyInstaller fails
- Make sure you're running from the project directory
- Try: `pip install --upgrade pyinstaller`

### Antivirus blocks the .exe
- This is common with PyInstaller executables
- Add an exception in your antivirus software
- Code signing (requires a certificate) can help with this

## Files in This Project

```
TraverseCalculator.py      # Main application source code
TraverseCalculator.spec    # PyInstaller configuration
installer.iss              # Inno Setup installer script
build_installer.bat        # Automated build script
BUILD_INSTRUCTIONS.md      # This file
updater.py                 # Auto-update module
version.json               # Version manifest for updates
```

## Auto-Update System

The application includes an automatic update system that checks GitHub for new versions.

### How It Works

1. **On startup**: The app checks `version.json` on GitHub (after a 3-second delay)
2. **Version comparison**: Compares local version with remote version
3. **User prompt**: If a newer version exists, prompts the user to download
4. **Manual check**: Users can also check via Help → Check for Updates

### Releasing a New Version

To release an update that users will receive automatically:

#### Step 1: Update Version Numbers

1. **Edit `version.json`**:
   ```json
   {
     "version": "1.1.0",
     "release_notes": "Description of what's new",
     "download_url": "https://github.com/Av1Sharma/TraverseCalculator/releases/latest",
     "release_date": "2026-01-15"
   }
   ```

2. **Edit `updater.py`** - Update `CURRENT_VERSION`:
   ```python
   CURRENT_VERSION = "1.1.0"
   ```

#### Step 2: Commit and Tag

```bash
git add .
git commit -m "Release v1.1.0 - description of changes"
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

#### Step 3: GitHub Actions Builds Automatically

- The workflow triggers on version tags (v*)
- Builds the executable and installer
- Creates a GitHub Release with the files attached
- Users running the old version will be notified!

### Important URLs

Make sure these are correct in `updater.py`:

```python
# Your GitHub raw URL for version.json
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Av1Sharma/TraverseCalculator/main/version.json"

# Your GitHub releases page
RELEASES_URL = "https://github.com/Av1Sharma/TraverseCalculator/releases/latest"
```

**Replace `Av1Sharma/TraverseCalculator`** with your actual GitHub username and repository name.

## Windows SmartScreen Warning

Windows may show "Windows protected your PC" for unsigned executables.

### Why This Happens
- Your executable is not code-signed
- Windows doesn't recognize the publisher

### Solutions

1. **Free: SignPath.io** (Open Source Projects Only)
   - https://signpath.io - free code signing for OSS
   - Requires your project to be public on GitHub

2. **User Workaround**
   - Click "More info" → "Run anyway"
   - This is normal for unsigned software

3. **Paid: Code Signing Certificate** (~$70-500/year)
   - Providers: DigiCert, Sectigo, SSL.com
   - EV certificates get immediate SmartScreen trust
