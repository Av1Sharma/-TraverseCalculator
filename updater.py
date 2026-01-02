"""
Auto-Update Module for Traverse Calculator
Checks GitHub for new versions and prompts user to update.
"""

import urllib.request
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox
import threading
import ssl
import os
import sys

# Current application version
CURRENT_VERSION = "1.0.0"

# GitHub raw URL for version.json in your repository
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Av1Sharma/-TraverseCalculator/main/version.json"

# GitHub releases page
RELEASES_URL = "https://github.com/Av1Sharma/-TraverseCalculator/releases/latest"


def get_version_tuple(version_str):
    """Convert version string to tuple for comparison (e.g., '1.2.3' -> (1, 2, 3))"""
    try:
        return tuple(int(x) for x in version_str.split('.'))
    except:
        return (0, 0, 0)


def is_newer_version(remote_version, local_version=CURRENT_VERSION):
    """Check if remote version is newer than local version"""
    return get_version_tuple(remote_version) > get_version_tuple(local_version)


def fetch_remote_version():
    """
    Fetch the version info from GitHub.
    Returns dict with version info or None if failed.
    """
    try:
        # Create SSL context that doesn't verify certificates (for Windows compatibility)
        # In production, you'd want proper SSL verification
        context = ssl.create_default_context()
        
        # Some systems have issues with SSL, so we try with and without verification
        try:
            with urllib.request.urlopen(GITHUB_RAW_URL, timeout=10, context=context) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except ssl.SSLError:
            # Fallback: try without SSL verification (not ideal but works)
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(GITHUB_RAW_URL, timeout=10, context=context) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
    except Exception as e:
        print(f"Update check failed: {e}")
        return None


def check_for_updates_sync():
    """
    Synchronously check for updates.
    Returns (has_update, remote_version_info) tuple.
    """
    remote_info = fetch_remote_version()
    
    if remote_info is None:
        return False, None
    
    remote_version = remote_info.get('version', '0.0.0')
    
    if is_newer_version(remote_version):
        return True, remote_info
    
    return False, remote_info


def show_update_dialog(parent, remote_info):
    """Show a dialog prompting the user to update"""
    version = remote_info.get('version', 'Unknown')
    release_notes = remote_info.get('release_notes', 'No release notes available.')
    download_url = remote_info.get('download_url', RELEASES_URL)
    
    message = (
        f"A new version of Traverse Calculator is available!\n\n"
        f"Current Version: {CURRENT_VERSION}\n"
        f"New Version: {version}\n\n"
        f"What's New:\n{release_notes}\n\n"
        f"Would you like to download the update now?"
    )
    
    result = messagebox.askyesno(
        "Update Available",
        message,
        parent=parent
    )
    
    if result:
        webbrowser.open(download_url)


def check_for_updates_async(parent, show_no_update_message=False):
    """
    Check for updates in a background thread.
    
    Args:
        parent: The parent tkinter window
        show_no_update_message: If True, show a message even if no update is available
    """
    def check_thread():
        has_update, remote_info = check_for_updates_sync()
        
        # Schedule UI updates on the main thread
        if has_update and remote_info:
            parent.after(0, lambda: show_update_dialog(parent, remote_info))
        elif show_no_update_message:
            parent.after(0, lambda: messagebox.showinfo(
                "No Updates",
                f"You are running the latest version ({CURRENT_VERSION}).",
                parent=parent
            ))
    
    # Run the check in a background thread so it doesn't block the UI
    thread = threading.Thread(target=check_thread, daemon=True)
    thread.start()


def check_for_updates_on_startup(parent, delay_ms=2000):
    """
    Schedule an update check after the app has started.
    
    Args:
        parent: The parent tkinter window
        delay_ms: Delay in milliseconds before checking (default 2 seconds)
    """
    parent.after(delay_ms, lambda: check_for_updates_async(parent, show_no_update_message=False))


# For testing the module directly
if __name__ == "__main__":
    print(f"Current version: {CURRENT_VERSION}")
    print("Checking for updates...")
    
    has_update, info = check_for_updates_sync()
    
    if has_update:
        print(f"Update available: {info.get('version')}")
        print(f"Release notes: {info.get('release_notes')}")
        print(f"Download: {info.get('download_url')}")
    elif info:
        print(f"You're up to date! (Latest: {info.get('version')})")
    else:
        print("Could not check for updates. Check your internet connection.")
