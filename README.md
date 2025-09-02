DellBIOSTools V2.1
==================

Requirements
------------
- Python 3.12 or greater is required to run the raw Python code (DellBiosTools.pyw)
- Windows 10/11 recommended for EXE build and usage

Preview
-------
https://github.com/user-attachments/assets/b83312c3-4174-4e01-85b5-47fa5a0c7f03

------------------------------------------------------------
🚀 Quick Build (Recommended)

To create a standalone EXE without worrying about Python setup:

1. Download this repo as ZIP and extract it.
2. Double-click:

    build_dellbiostools.bat

3. The script will:
   - Check if Python 3.12+ is installed
   - If missing, install it automatically (via Winget or python.org)
   - Upgrade pip and install PyInstaller
   - Compile DellBiosTools.pyw into DellBiosTools.exe
   - Place the finished EXE in the project folder

When it finishes, you’ll see:

    DellBiosTools.exe

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

4. Build the EXE:

   pyinstaller --noconfirm --onefile --windowed DellBiosTools.pyw

5. The EXE will appear at:

   dist\DellBiosTools.exe

6. (Optional) Clean up temporary build files:

   rmdir /s /q build
   rmdir /s /q dist
   del DellBiosTools.spec

------------------------------------------------------------
🛠 Usage

This tool combines three essential utilities for Dell BIOS management:

1. Dell (8FC8 Patcher)
   - Helps unlock Dell BIOS by patching specific patterns
   - Works with 8FC8 suffix systems

   Steps:
   - Click "Browse" to select your BIOS file
   - Click "Patch BIOS" to apply the patch
   - After patching, update your device with the patched BIOS file and reboot
   - When prompted that "The Service Tag has not been programmed", input your Service Tag
   - The device will reboot again and should boot to Windows

2. Password Generator
   - Generates master passwords for Dell systems based on service tag
   - Supports multiple tag types (595B, D35B, 2A7B, 1D3B, 1F66, etc.)

   Steps:
   - Enter your 7-character Dell Service Tag followed by the 4-character tag suffix
   - Click "Compute Password" to generate the BIOS master password
   - Use the generated password to unlock your Dell system

3. Service Tag Extractor
   - Extracts Service Tag values from .bin BIOS files

   Steps:
   - Load your Dell .bin file
   - Click "Extract Tags" (this may take some time)

------------------------------------------------------------
⚠️ Disclaimer

This tool is provided as-is with no warranty of any kind.
Use at your own risk. The authors and contributors are not responsible
for any data loss, corruption, hardware damage, or other issues that may occur
from the use of this program.

👉 Always back up your BIOS before patching and test in a safe environment.

------------------------------------------------------------
📜 License

MIT — free to use, share, and modify

------------------------------------------------------------
Credits

- Original tools by Rex98 & Techshack Cebu
- Research by Dogbert and Asyncritus
- Python scripts courtesy of chromebreakerdev
