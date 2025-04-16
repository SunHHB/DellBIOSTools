import os
from collections import defaultdict

def is_ascii_upper_alnum_utf16le(data):
    if len(data) != 14:
        return False
    for i in range(0, 14, 2):
        char = data[i]
        if not (48 <= char <= 57 or 65 <= char <= 90):  # 0–9 or A–Z
            return False
        if data[i+1] != 0x00:
            return False
    return True

def scan_utf16le_tags_and_rank(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    print("=== Dell BIOS UTF-16LE Service Tag Frequency Analyzer ===\n")
    tags = defaultdict(list)

    for i in range(len(data) - 16):
        chunk = data[i:i+14]
        terminator = data[i+14:i+16]

        if is_ascii_upper_alnum_utf16le(chunk) and terminator == b'\x00\x00':
            try:
                tag = chunk.decode('utf-16le')
                tags[tag].append(i)
            except:
                continue

    if not tags:
        print("❌ No valid tags found.")
        return

    print("=== Service Tag Occurrence Summary ===")
    sorted_tags = sorted(tags.items(), key=lambda x: -len(x[1]))
    for tag, offsets in sorted_tags:
        print(f"Tag: {tag} | Found: {len(offsets)} times | Example Offset: 0x{offsets[0]:08X}")

    most_common = sorted_tags[0]
    print("\n✅ Most Likely Service Tag:", most_common[0])
    print(f"   Occurrences: {len(most_common[1])}")
    print(f"   Region Range: 0x{min(most_common[1]):08X} – 0x{max(most_common[1]):08X}")

if __name__ == '__main__':
    print("=== True Dell BIOS Service Tag Extractor ===")
    bin_file = input("Enter BIOS dump filename (e.g. BIOS.bin): ").strip()
    if os.path.isfile(bin_file):
        scan_utf16le_tags_and_rank(bin_file)
    else:
        print("[ERROR] File not found.")
    input("\nDone. Press Enter to close...")
