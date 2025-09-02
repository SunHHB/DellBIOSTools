
# DellBIOSTools V2.1

Requirements:
-------------
- Python 3.12 or greater is required to run the Python code 

Preview:
--------
https://github.com/user-attachments/assets/b83312c3-4174-4e01-85b5-47fa5a0c7f03

------------------------------------------------------------
🚀 Quick Build (Recommended)

To create the EXE without worrying about Python setup:

1. Download this repo as ZIP and extract it.
2. Double-click:

    builddellbiostools_exe.bat

3. The script will:
   - Check if Python 3.12+ is installed
   - If missing, install it automatically (via Winget or python.org)
   - Install PyInstaller
   - Build dellbiostools.exe in the project folder

When it finishes, you’ll see:

    dellbiostools.exe

in the same folder. ✅

------------------------------------------------------------
🔧 Manual Build (Advanced)

If you prefer to build manually:

1. Install Python 3.12+ from:  
   https://www.python.org/downloads/release/python-3120/  
   (Check “Add Python to PATH” during install)

2. Open Command Prompt in this repo folder.

3. Upgrade pip and install PyInstaller:

   pip install --upgrade pip
   pip install pyinstaller

4. Build the exe:

   pyinstaller --noconfirm --onefile --windowed dellbiostools.py

5. The exe will appear at:

   dist\dellbiostools.exe

6. (Optional) Clean up:

   rmdir /s /q build
   rmdir /s /q dist
   del dellbiostools.spec

------------------------------------------------------------
⚠️ Disclaimer

This tool is provided **as-is** with no warranty of any kind.  
Use at your own risk. The authors and contributors are not responsible  
for any data loss, corruption, hardware damage, or other issues that may occur  
from the use of this program. Always test in a safe environment before deploying.

------------------------------------------------------------
📜 License

MIT — free to use, share, and modify
