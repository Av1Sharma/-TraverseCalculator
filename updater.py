"""
Auto-Update Module for Traverse Calculator
Downloads and installs updates automatically from GitHub.
"""

import urllib.request
import json
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import ssl
import os
import sys
import tempfile
import subprocess

# Current application version
CURRENT_VERSION = "1.0.0"

# GitHub URLs
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Av1Sharma/-TraverseCalculator/main/version.json"
RELEASES_URL = "https://github.com/Av1Sharma/-TraverseCalculator/releases/latest"

# Direct download URL template for releases
# This will be constructed from the version tag
DOWNLOAD_URL_TEMPLATE = "https://github.com/Av1Sharma/-TraverseCalculator/releases/download/v{version}/TraverseCalculator.exe"


def get_version_tuple(version_str):
    """Convert version string to tuple for comparison"""
    try:
        return tuple(int(x) for x in version_str.split('.'))
    except:
        return (0, 0, 0)


def is_newer_version(remote_version, local_version=CURRENT_VERSION):
    """Check if remote version is newer than local version"""
    return get_version_tuple(remote_version) > get_version_tuple(local_version)


def get_ssl_context():
    """Get SSL context, with fallback for systems with SSL issues"""
    try:
        return ssl.create_default_context()
    except:
        return ssl._create_unverified_context()


def fetch_remote_version():
    """Fetch the version info from GitHub."""
    try:
        context = get_ssl_context()
        try:
            with urllib.request.urlopen(GITHUB_RAW_URL, timeout=10, context=context) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except ssl.SSLError:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(GITHUB_RAW_URL, timeout=10, context=context) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
    except Exception as e:
        print(f"Update check failed: {e}")
        return None


def check_for_updates_sync():
    """Synchronously check for updates. Returns (has_update, remote_version_info) tuple."""
    remote_info = fetch_remote_version()
    
    if remote_info is None:
        return False, None
    
    remote_version = remote_info.get('version', '0.0.0')
    
    if is_newer_version(remote_version):
        return True, remote_info
    
    return False, remote_info


def get_current_exe_path():
    """Get the path to the current executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as script (for testing)
        return os.path.abspath(__file__)


def download_update(version, progress_callback=None):
    """
    Download the new version from GitHub.
    Returns the path to the downloaded file, or None if failed.
    """
    download_url = DOWNLOAD_URL_TEMPLATE.format(version=version)
    
    try:
        context = get_ssl_context()
        
        # Create temp file for download
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"TraverseCalculator_v{version}.exe")
        
        # Open URL and get content length
        request = urllib.request.Request(download_url)
        with urllib.request.urlopen(request, timeout=60, context=context) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            block_size = 8192
            
            with open(temp_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    downloaded += len(buffer)
                    
                    if progress_callback and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        progress_callback(progress)
        
        return temp_path
    
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def create_update_batch_script(new_exe_path, current_exe_path):
    """
    Create a batch script that will:
    1. Wait for the current app to close
    2. Replace the old exe with the new one
    3. Restart the app
    """
    batch_content = f'''@echo off
echo Updating Traverse Calculator...
echo Please wait...

REM Wait for the old process to exit (up to 10 seconds)
set /a count=0
:waitloop
tasklist /FI "IMAGENAME eq {os.path.basename(current_exe_path)}" 2>NUL | find /I "{os.path.basename(current_exe_path)}" >NUL
if "%ERRORLEVEL%"=="0" (
    set /a count+=1
    if %count% lss 20 (
        timeout /t 1 /nobreak >NUL
        goto waitloop
    )
)

REM Small delay to ensure file handles are released
timeout /t 2 /nobreak >NUL

REM Replace the old executable
echo Replacing old version...
copy /Y "{new_exe_path}" "{current_exe_path}"

if %ERRORLEVEL% neq 0 (
    echo Update failed! Please try again.
    pause
    exit /b 1
)

REM Clean up the downloaded file
del "{new_exe_path}"

REM Restart the application
echo Starting updated application...
start "" "{current_exe_path}"

REM Self-delete this batch file
del "%~f0"
'''
    
    # Write batch file to temp directory
    batch_path = os.path.join(tempfile.gettempdir(), "traverse_update.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    return batch_path


def perform_update(new_exe_path, parent_window=None):
    """
    Perform the actual update by launching the batch script and exiting.
    """
    current_exe = get_current_exe_path()
    
    # Create the update batch script
    batch_path = create_update_batch_script(new_exe_path, current_exe)
    
    # Launch the batch script (hidden window)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    # Exit the current application
    if parent_window:
        parent_window.destroy()
    sys.exit(0)


class UpdateDialog:
    """Dialog that shows download progress and handles the update"""
    
    def __init__(self, parent, remote_info):
        self.parent = parent
        self.remote_info = remote_info
        self.version = remote_info.get('version', 'Unknown')
        self.cancelled = False
        
    def show(self):
        """Show the update confirmation dialog"""
        release_notes = self.remote_info.get('release_notes', 'Bug fixes and improvements.')
        
        message = (
            f"A new version is available!\n\n"
            f"Current: v{CURRENT_VERSION}\n"
            f"New: v{self.version}\n\n"
            f"What's New:\n{release_notes}\n\n"
            f"Install the update now?"
        )
        
        result = messagebox.askyesno(
            "Update Available",
            message,
            parent=self.parent
        )
        
        if result:
            self.start_download()
    
    def start_download(self):
        """Start the download with a progress dialog"""
        # Create progress window
        self.progress_window = tk.Toplevel(self.parent)
        self.progress_window.title("Updating...")
        self.progress_window.geometry("350x120")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.parent)
        self.progress_window.grab_set()
        
        # Center the window
        self.progress_window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 175
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 60
        self.progress_window.geometry(f"+{x}+{y}")
        
        # Add widgets
        frame = ttk.Frame(self.progress_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(frame, text=f"Downloading v{self.version}...")
        self.status_label.pack(pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(frame, length=300, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        
        self.percent_label = ttk.Label(frame, text="0%")
        self.percent_label.pack()
        
        # Prevent closing
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Start download in background thread
        thread = threading.Thread(target=self._download_thread, daemon=True)
        thread.start()
    
    def _update_progress(self, progress):
        """Update the progress bar (called from download thread)"""
        self.progress_window.after(0, lambda: self._set_progress(progress))
    
    def _set_progress(self, progress):
        """Set progress bar value (must be called from main thread)"""
        self.progress_bar['value'] = progress
        self.percent_label.config(text=f"{int(progress)}%")
    
    def _download_thread(self):
        """Background thread that downloads the update"""
        new_exe_path = download_update(self.version, self._update_progress)
        
        if new_exe_path and os.path.exists(new_exe_path):
            # Download successful - perform update
            self.progress_window.after(0, lambda: self._finish_update(new_exe_path))
        else:
            # Download failed
            self.progress_window.after(0, self._download_failed)
    
    def _finish_update(self, new_exe_path):
        """Finish the update process"""
        self.status_label.config(text="Installing update...")
        self.progress_window.update()
        
        # Close progress window
        self.progress_window.destroy()
        
        # Show restart message
        messagebox.showinfo(
            "Update Ready",
            "The update has been downloaded.\n\n"
            "The application will now restart to complete the installation.",
            parent=self.parent
        )
        
        # Perform the update (this will exit the app)
        perform_update(new_exe_path, self.parent)
    
    def _download_failed(self):
        """Handle download failure"""
        self.progress_window.destroy()
        messagebox.showerror(
            "Update Failed",
            "Failed to download the update.\n\n"
            "Please check your internet connection and try again.",
            parent=self.parent
        )


def show_update_dialog(parent, remote_info):
    """Show the update dialog"""
    dialog = UpdateDialog(parent, remote_info)
    dialog.show()


def check_for_updates_async(parent, show_no_update_message=False):
    """Check for updates in a background thread."""
    def check_thread():
        has_update, remote_info = check_for_updates_sync()
        
        if has_update and remote_info:
            parent.after(0, lambda: show_update_dialog(parent, remote_info))
        elif show_no_update_message:
            parent.after(0, lambda: messagebox.showinfo(
                "No Updates",
                f"You are running the latest version (v{CURRENT_VERSION}).",
                parent=parent
            ))
    
    thread = threading.Thread(target=check_thread, daemon=True)
    thread.start()


def check_for_updates_on_startup(parent, delay_ms=2000):
    """Schedule an update check after the app has started."""
    parent.after(delay_ms, lambda: check_for_updates_async(parent, show_no_update_message=False))


# For testing
if __name__ == "__main__":
    print(f"Current version: {CURRENT_VERSION}")
    print("Checking for updates...")
    
    has_update, info = check_for_updates_sync()
    
    if has_update:
        print(f"Update available: {info.get('version')}")
        print(f"Download URL: {DOWNLOAD_URL_TEMPLATE.format(version=info.get('version'))}")
    elif info:
        print(f"You're up to date! (Latest: {info.get('version')})")
    else:
        print("Could not check for updates.")
