Dell BIOS Tools
==============

This tool combines two essential utilities for Dell BIOS management:

1. Dell (8FC8 Patcher)
   - Helps unlock Dell BIOS by patching specific patterns
   - Works with 8FC8 suffix systems

2. Password Generator
   - Generates master passwords for Dell systems based on service tag
   - Supports multiple tag types (595B, D35B, 2A7B, 1D3B, 1F66, etc.)

Instructions:
------------
- Run Dell_8FC8_Patcher.pyw to start the application
- Patched BIOS files will be saved in path displayed in window
- Use the tabs at the top to switch between tools

For instructions on how to use the ch341a Bios programmer, you can go here..https://winraid.level1techs.com/t/guide-flash-bios-with-ch341a-programmer/32948 

YOU SHOULD ALWAYS SAVE A BACKUP OF YOUR ORIGINAL BIOS BIN FILE BEFORE PATCHING !

For BIOS Unlocker:
1. Click "Browse" to select your BIOS file
2. Click "Patch BIOS" to apply the patch
3. After patching, you'll need to update your device with the patched bios file and reboot 
4. When prompted that "The Service Tag has not been programmed", input your Service Tag
5. The device will reboot again and you should be able to boot to Windows


For Password Generator:
1. Enter your 7-character Dell Service Tag followed by the 4-character tag suffix
2. Click "Compute Password" to generate the BIOS master password
3. Use the generated password to unlock your Dell system

NOTE: Use at your own risk. Improper BIOS modification can damage your system.

Based on the original tools by Rex98 & Techshack Cebu 
Based on research by Dogbert and Asyncritus. Python scripts courtesy of chromebreakerdev.
