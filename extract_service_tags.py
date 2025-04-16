import os
import re

def is_valid_tag(s):
    return (
        len(s) == 7 and
        all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for c in s)
        and s not in {"0000000", "1111111", "AAAAAAA", "FFFFFFF", "1234567"}
    )

def extract_ascii(b):
    return ''.join([chr(c) if 32 <= c <= 126 else '.' for c in b])

def scan_for_clean_model_tag_pairs(filepath):
    if not os.path.isfile(filepath):
        print("[ERROR] File not found:", filepath)
        return

    with open(filepath, 'rb') as f:
        data = f.read()

    results = []

    i = 0
    while i < len(data) - 64:
        tag_bytes = data[i:i+7]
        try:
            tag = tag_bytes.decode('ascii')
        except:
            i += 1
            continue

        if not is_valid_tag(tag):
            i += 1
            continue

        # Lookahead for actual model identifier
        lookahead = data[i+7:i+40]
        lookahead_ascii = extract_ascii(lookahead)

        # Stronger regex: must start with "/" and be followed by 5+ alnum chars
        model_match = re.search(r'/(CN|DL|DH|FM|IN|HK)[A-Z0-9]{4,12}', lookahead_ascii)
        if model_match:
            model_str = model_match.group(0)
            results.append((i, tag, model_str))
            # Skip over the matched block to prevent sliding window noise
            i += 40
        else:
            i += 1

    if not results:
        print("\nNo clean service tag + model matches found.")
        return

    print("\n=== Final Filtered Service Tag Matches ===")
    for offset, tag, model in results:
        print("Offset 0x{:08X} | Tag: {:7} | Model: {}".format(offset, tag, model))

if __name__ == '__main__':
    print("=== Dell BIOS Service Tag + Model Extractor ===")
    bin_file = input("Enter BIOS dump filename: ").strip()
    scan_for_clean_model_tag_pairs(bin_file)
    input("\nPress Enter to close...")
