import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import re
import os
import binascii
import subprocess
import hashlib
from typing import List, Dict

################################################################################
# PART 1: BIOS Unlocker Tool Functions
################################################################################

def convert_hex_to_bytes(hex_string):
    """Convert hex string to byte array"""
    try:
        return bytes.fromhex(hex_string)
    except binascii.Error as e:
        return None

def bytes_to_hex_string(byte_array):
    """Convert byte array to hex string without separators"""
    return byte_array.hex().upper()

def find_intel_signature(data, signature_bytes):
    """Find Intel signature in the first 0x1000 bytes"""
    for i in range(min(0x1000, len(data) - len(signature_bytes))):
        if data[i:i+len(signature_bytes)] == signature_bytes:
            return i
    return -1

def find_pattern_matches(data, pattern_regex):
    """Find all matches of the regex pattern in the data, but only up to offset 0x160000"""
    matches = []
    
    max_offset = min(0x160000, len(data))
    for i in range(max_offset):
        chunk_size = min(20, len(data) - i)
        if chunk_size < 6:
            continue
            
        chunk = data[i:i+chunk_size]
        hex_chunk = bytes_to_hex_string(chunk)
        
        match = re.match(pattern_regex, hex_chunk)
        if match:
            matches.append(i)
    
    return matches

################################################################################
# PART 2: Dell Password Generator Functions
################################################################################

md5magic = [
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
]

md5magic2 = [
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039
]

rotationTable = [
    [7, 12, 17, 22],
    [5, 9, 14, 20],
    [4, 11, 16, 23],
    [6, 10, 15, 21]
]

initialData = [
    0x67452301,
    0xEFCDAB89,
    0x98BADCFE,
    0x10325476
]

def mask32(x: int) -> int:
    return x & 0xFFFFFFFF

def rol(x: int, bits: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << bits) & 0xFFFFFFFF) | (x >> (32 - bits))

# The "enc" functions
def encF1(num1: int, num2: int) -> int:
    return (num1 + num2) & 0xFFFFFFFF

def encF1N(num1: int, num2: int) -> int:
    return (num1 - num2) & 0xFFFFFFFF

def encF2(num1: int, num2: int, num3: int) -> int:
    return ((num3 ^ num2) & num1) ^ num3

def encF2N(num1: int, num2: int, num3: int) -> int:
    return encF2(num1, num2, (~num3) & 0xFFFFFFFF)

def encF3(num1: int, num2: int, num3: int) -> int:
    return ((num1 ^ num2) & num3) ^ num2

def encF4(num1: int, num2: int, num3: int) -> int:
    return (num2 ^ num1) ^ num3

def encF4N(num1: int, num2: int, num3: int) -> int:
    return encF4(num1, (~num2) & 0xFFFFFFFF, num3)

def encF5(num1: int, num2: int, num3: int) -> int:
    return (num1 | ((~num3) & 0xFFFFFFFF)) ^ num2

def encF5N(num1: int, num2: int, num3: int) -> int:
    return encF5((~num1) & 0xFFFFFFFF, num2, num3)

class Tag595BEncoder:
    f1 = staticmethod(encF1N)
    f2 = staticmethod(encF2N)
    f3 = staticmethod(encF3)
    f4 = staticmethod(encF4N)
    f5 = staticmethod(encF5N)

    md5table = md5magic

    def __init__(self, encBlock: List[int]):
        self.encBlock = encBlock
        self.encData = self.initialData()
        self.A = self.encData[0]
        self.B = self.encData[1]
        self.C = self.encData[2]
        self.D = self.encData[3]

    @classmethod
    def encode(cls, encBlock: List[int]) -> List[int]:
        obj = cls(encBlock)
        obj.makeEncode()
        return obj.result()

    def makeEncode(self) -> None:
        for i in range(64):
            which = i >> 4
            if which == 0:
                t = self.calculate(self.f2, (i & 15), i)
            elif which == 1:
                t = self.calculate(self.f3, ((i*5+1)&15), i)
            elif which == 2:
                t = self.calculate(self.f4, ((i*3+5)&15), i)
            else:
                t = self.calculate(self.f5, ((i*7)&15), i)
            oldA = self.A
            self.A = self.D
            self.D = self.C
            self.C = self.B
            shift = rotationTable[which][(i &3)]
            self.B = mask32(self.B + rol(t, shift))

        self.incrementData()

    def initialData(self) -> List[int]:
        return initialData[:]

    def calculate(self, func, key1: int, key2: int) -> int:
        tmp = func(self.B, self.C, self.D)
        combined = (self.md5table[key2] + self.encBlock[key1]) & 0xFFFFFFFF
        return (self.A + self.f1(tmp, combined)) & 0xFFFFFFFF

    def incrementData(self) -> None:
        self.encData[0] = mask32(self.encData[0] + self.A)
        self.encData[1] = mask32(self.encData[1] + self.B)
        self.encData[2] = mask32(self.encData[2] + self.C)
        self.encData[3] = mask32(self.encData[3] + self.D)

    def result(self) -> List[int]:
        return [mask32(x) for x in self.encData]

class TagD35BEncoder(Tag595BEncoder):
    f1 = staticmethod(encF1)
    f2 = staticmethod(encF2)
    f3 = staticmethod(encF3)
    f4 = staticmethod(encF4)
    f5 = staticmethod(encF5)

class Tag1D3BEncoder(Tag595BEncoder):
    def makeEncode(self) -> None:
        for j in range(21):
            self.A |= 0x97
            self.B ^= 0x8
            self.C |= (0x60606161 - j) & 0xFFFFFFFF
            self.D ^= (0x50501010 + j) & 0xFFFFFFFF
            super().makeEncode()

class Tag1F66Encoder(Tag595BEncoder):
    md5table = md5magic2

    def makeEncode(self) -> None:
        t = 0
        # first loop => 17 times
        for j in range(17):
            self.A |= 0x100097
            self.B ^= 0xA0008
            self.C |= (0x60606161 - j) & 0xFFFFFFFF
            self.D ^= (0x50501010 + j) & 0xFFFFFFFF

            for i in range(64):
                which = i>>4
                if which == 0:
                    t = self.calculate(self.f2, (i &15), (i+16)&0xFFFFFFFF)
                elif which == 1:
                    t = self.calculate(self.f3, ((i*5+1)&15), (i+32)&0xFFFFFFFF)
                elif which == 2:
                    offset = i -2*(i &12)+12
                    t = self.calculate(self.f4, ((i*3+5)&15), offset)
                else:
                    offset = 2*(i &3) - (i &15)+12
                    t = self.calculate(self.f5, ((i*7)&15), offset)
                oldA = self.A
                self.A = self.D
                self.D = self.C
                self.C = self.B
                shift = rotationTable[which][(i &3)]
                self.B = mask32(self.B + rol(t, shift))
            self.incrementData()

        # second => 21 times
        for j in range(21):
            self.A |= 0x97
            self.B ^= 0x8
            self.C |= (0x50501010 - j)&0xFFFFFFFF
            self.D ^= (0x60606161 + j)&0xFFFFFFFF

            for i in range(64):
                which = i>>4
                if which == 0:
                    offset = 2*(i &3) - i + 44
                    t = self.calculate(self.f4, ((i*3+5)&15), offset)
                elif which == 1:
                    offset = 2*(i &3) - i +76
                    t = self.calculate(self.f5, ((i*7)&15), offset)
                elif which == 2:
                    offset = (i &15)
                    t = self.calculate(self.f2, (i &15), offset)
                else:
                    offset = (i -32)&0xFFFFFFFF
                    t = self.calculate(self.f3, ((i*5+1)&15), offset)
                g = ((i>>4)+2)&3
                oldA = self.A
                self.A = self.D
                self.D = self.C
                self.C = self.B
                shift = rotationTable[g][(i &3)]
                self.B = mask32(self.B + rol(t, shift))
            self.incrementData()

class Tag6FF1Encoder(Tag595BEncoder):
    md5table = md5magic2
    counter1 = 23

    def makeEncode(self) -> None:
        t=0
        # first => self.counter1
        for j in range(self.counter1):
            self.A |= 0xA08097
            self.B ^= 0xA010908
            self.C |= (0x60606161 - j)&0xFFFFFFFF
            self.D ^= (0x50501010 + j)&0xFFFFFFFF

            for i in range(64):
                which = i>>4
                k = (i &15) - ((i &12)<<1) +12
                if which == 0:
                    t = self.calculate(self.f2, (i &15), (i+32)&0xFFFFFFFF)
                elif which == 1:
                    t = self.calculate(self.f3, ((i*5+1)&15), (i&15))
                elif which == 2:
                    t = self.calculate(self.f4, ((i*3+5)&15), (k+16)&0xFFFFFFFF)
                else:
                    t = self.calculate(self.f5, ((i*7)&15), (k+48)&0xFFFFFFFF)
                oldA = self.A
                self.A = self.D
                self.D = self.C
                self.C = self.B
                shift = rotationTable[which][(i &3)]
                self.B = mask32(self.B + rol(t, shift))
            self.incrementData()

        # second => 17
        for j in range(17):
            self.A |= 0x100097
            self.B ^= 0xA0008
            self.C |= (0x50501010 - j)&0xFFFFFFFF
            self.D ^= (0x60606161 + j)&0xFFFFFFFF

            for i in range(64):
                which = i>>4
                k = (i &15) - ((i &12)<<1) +12
                if which == 0:
                    shiftval = ((i &15)*3 +5)&15
                    t = self.calculate(self.f4, shiftval, (k+16))
                elif which == 1:
                    shiftval = ((i &3)*7 + (i &12)+4)&15
                    t = self.calculate(self.f5, shiftval, ((i &15)+32)&0xFFFFFFFF)
                elif which == 2:
                    t = self.calculate(self.f2, (k &15), k)
                else:
                    shiftval = ((i &15)*5 +1)&15
                    t = self.calculate(self.f3, shiftval, ((i &15)+48)&0xFFFFFFFF)
                g = ((i>>4)+2)&3
                oldA = self.A
                self.A = self.D
                self.D = self.C
                self.C = self.B
                shift = rotationTable[g][(i &3)]
                self.B = mask32(self.B + rol(t, shift))
            self.incrementData()

class Tag1F5AEncoder(Tag595BEncoder):
    md5table = md5magic2
    def makeEncode(self) -> None:
        for _ in range(5):
            for j in range(64):
                k = 12 + (j &3) - (j &12)
                which = j>>4
                if which == 0:
                    t = self.calculate(self.f2, j &15, j)
                elif which == 1:
                    t = self.calculate(self.f3, ((j*5+1)&15), j)
                elif which == 2:
                    t = self.calculate(self.f4, ((j*3+5)&15), (k+0x20)&0xFFFFFFFF)
                else:
                    t = self.calculate(self.f5, ((j*7)&15), (k+0x30)&0xFFFFFFFF)
                oldB = self.B
                self.B = self.D
                self.D = self.A
                self.A = self.C
                shift = rotationTable[which][(j &3)]
                self.C = mask32(self.C + rol(t, shift))
            self.incrementData()

    def incrementData(self) -> None:
        self.encData[0] = mask32(self.encData[0] + self.B)
        self.encData[1] = mask32(self.encData[1] + self.C)
        self.encData[2] = mask32(self.encData[2] + self.A)
        self.encData[3] = mask32(self.encData[3] + self.D)

    def calculate(self, func, key1: int, key2: int) -> int:
        tmp = func(self.C, self.A, self.D)
        combined = (self.md5table[key2] + self.encBlock[key1]) &0xFFFFFFFF
        return (self.B + encF1(tmp, combined)) &0xFFFFFFFF

class TagBF97Encoder(Tag6FF1Encoder):
    counter1 = 31

class TagE7A8Encoder(Tag595BEncoder):
    md5table = md5magic2
    loopParams = [17,13,12,8]
    encodeParams = [
        0x50501010, 0xA010908, 0xA08097, 0x60606161,
        0x60606161, 0xA0008,  0x100097, 0x50501010
    ]
    def initialData(self) -> List[int]:
        return [0,0,0,0]

    def makeEncode(self) -> None:
        for p in range(self.loopParams[0]):  #17
            self.A |= self.encodeParams[0]
            self.B ^= self.encodeParams[1]
            self.C |= (self.encodeParams[2]-p)&0xFFFFFFFF
            self.D ^= (self.encodeParams[3]+p)&0xFFFFFFFF

            for j in range(0, self.loopParams[2], 4):
                self.shortcut(self.f2, j, j+32, 0, [0,1,2,3])
            for j in range(0, self.loopParams[2], 4):
                self.shortcut(self.f3, j, j, 1, [1,-2,-1,0])
            for j in range(self.loopParams[3],3,-4):
                self.shortcut(self.f4, j, j+16, 2, [-3,-4,-1,2])
            for j in range(self.loopParams[3],3,-4):
                self.shortcut(self.f5, j, j+48, 3, [2,3,2,-3])

            self.incrementData()

        for p in range(self.loopParams[1]):  #13
            self.A |= self.encodeParams[4]
            self.B ^= self.encodeParams[5]
            self.C |= (self.encodeParams[6]-p)&0xFFFFFFFF
            self.D ^= (self.encodeParams[7]+p)&0xFFFFFFFF

            for j in range(self.loopParams[3],3,-4):
                self.shortcut(self.f4, j, j+16, 2, [-3,-4,-1,2])
            for j in range(0,self.loopParams[2],4):
                self.shortcut(self.f5, j, j+32, 3, [2,3,2,-3])
            for j in range(self.loopParams[3],0,-4):
                self.shortcut(self.f2, j, j, 0, [0,1,2,3])
            for j in range(0,self.loopParams[2],4):
                self.shortcut(self.f3, j, j+48, 1, [1,-2,3,0])

            self.incrementData()

    def shortcut(self, fun, j, md5_index, rot_index, indexes):
        for i in range(4):
            t = self.calculate(fun, (j + indexes[i]) &7, md5_index + i)
            oldA = self.A
            self.A = self.D
            self.D = self.C
            self.C = self.B
            shift = rotationTable[rot_index][i]
            self.B = (self.B + rol(t, shift)) &0xFFFFFFFF

class TagE7A8EncoderSecond(TagE7A8Encoder):
    def __init__(self, encBlock: List[int]):
        super().__init__(encBlock)
        overfillArr = [
            (0xa0008 ^ 0x6d2f93a5),
            (0xa08097 ^ 0x6d2f93a5),
            (0xa010908 ^ 0x6d2f93a5),
            (0x60606161 ^ 0x6d2f93a5)
        ]
        extended = md5magic2[:] + overfillArr
        self.md5table = extended
        self.loopParams = [17,13,12,16]

class DellTag:
    Tag595B = "595B"
    TagD35B = "D35B"
    Tag2A7B = "2A7B"
    TagA95B = "A95B"
    Tag1D3B = "1D3B"
    Tag1F66 = "1F66"
    Tag6FF1 = "6FF1"
    Tag1F5A = "1F5A"
    TagBF97 = "BF97"
    TagE7A8 = "E7A8"

encoders: Dict[str,object] = {
    DellTag.Tag595B: Tag595BEncoder,
    DellTag.Tag2A7B: Tag595BEncoder,
    DellTag.TagA95B: Tag595BEncoder,
    DellTag.Tag1D3B: Tag1D3BEncoder,
    DellTag.TagD35B: TagD35BEncoder,
    DellTag.Tag1F66: Tag1F66Encoder,
    DellTag.Tag6FF1: Tag6FF1Encoder,
    DellTag.Tag1F5A: Tag1F5AEncoder,
    DellTag.TagBF97: TagBF97Encoder,
    DellTag.TagE7A8: TagE7A8Encoder,
}

# Scanner and character tables
scanCodes = (
    "\0\x1B1234567890-=\x08\x09"
    "qwertyuiop[]\x0D\xFF"
    "asdfghjkl;'`\xFF\\"
    "zxcvbnm,./"
)
encscans = [
    0x05,0x10,0x13,0x09,0x32,0x03,0x25,0x11,0x1F,0x17,0x06,0x15,
    0x30,0x19,0x26,0x22,0x0A,0x02,0x2C,0x2F,0x16,0x14,0x07,0x18,
    0x24,0x23,0x31,0x20,0x1E,0x08,0x2D,0x21,0x04,0x0B,0x12,0x2E
]
asciiPrintable = "012345679abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0"
extraCharacters = {
    "2A7B": asciiPrintable,
    "1F5A": asciiPrintable,
    "1D3B": "0BfIUG1kuPvc8A9Nl5DLZYSno7Ka6HMgqsJWm65yCQR94b21OTp7VFX2z0jihE33d4xtrew0",
    "1F66": "0ewr3d4xtUG1ku0BfIp7VFb21OTSno7KDLZYqsJWa6HMgCQR94m65y9Nl5Pvc8AjihE3X2z0",
    "6FF1": "08rptBxfbGVMz38IiSoeb360MKcLf4QtBCbWVzmH5wmZUcRR5DZG2xNCEv1nFtzsZB2bw1X0",
    "BF97": "0Q2drGk99rkQFMxN[Z5y3DGr16h638myIL2rzz2pzcU7JWLJ1EGnqRN4seZPRM2aBXIjbkGZ"
}

class SuffixType:
    ServiceTag = 0

def blockEncode(encBlock: List[int], tag: str) -> List[int]:
    if tag not in encoders:
        raise ValueError(f"Unknown tag: {tag}")
    klass = encoders[tag]
    return klass.encode(encBlock)

def byteArrayToInt(arr: List[int]) -> List[int]:
    resultLength = len(arr)>>2
    out = []
    for i in range(resultLength+1):
        val=0
        if i*4 < len(arr):
            val |= arr[i*4]
        if i*4+1 < len(arr):
            val |= (arr[i*4+1]<<8)
        if i*4+2 < len(arr):
            val |= (arr[i*4+2]<<16)
        if i*4+3 < len(arr):
            val |= (arr[i*4+3]<<24)
        val&=0xFFFFFFFF
        out.append(val)
    return out

def intArrayToByte(arr: List[int]) -> List[int]:
    out=[]
    for num in arr:
        out.append(num&0xFF)
        out.append((num>>8)&0xFF)
        out.append((num>>16)&0xFF)
        out.append((num>>24)&0xFF)
    return out

def calculateSuffix(serial: List[int], tag: str, type_: int) -> List[int]:
    suffix = [0]*8
    arr1 = []
    arr2 = []
    if type_ == SuffixType.ServiceTag:
        arr1 = [1,2,3,4]
        arr2 = [4,3,2]
    suffix[0] = serial[arr1[3]]
    suffix[1] = (serial[arr1[3]]>>5) | (((serial[arr1[2]]>>5)|(serial[arr1[2]]<<3)) & 0xF1)
    suffix[2] = serial[arr1[2]]>>2
    suffix[3] = (serial[arr1[2]]>>7)|(serial[arr1[1]]<<1)
    suffix[4] = (serial[arr1[1]]>>4)|(serial[arr1[0]]<<4)
    suffix[5] = serial[1]>>1
    suffix[6] = (serial[1]>>6)|(serial[0]<<2)
    suffix[7] = serial[0]>>3
    for i in range(8):
        suffix[i] &= 0xFF
    table = extraCharacters.get(tag, None)
    if table is not None:
        codesTable = [ord(c) for c in table]
    else:
        codesTable = encscans
    for i in range(8):
        r = 0xAA
        if suffix[i] &1:
            r ^= serial[arr2[0]]
        if suffix[i] &2:
            r ^= serial[arr2[1]]
        if suffix[i] &4:
            r ^= serial[arr2[2]]
        if suffix[i] &8:
            r ^= serial[1]
        if suffix[i] &16:
            r ^= serial[0]
        suffix[i] = codesTable[r % len(codesTable)]
    return suffix

def resultToString(arr: List[int], tag: str) -> str:
    r = arr[0] %9
    result = ""
    table = extraCharacters.get(tag, None)
    for i in range(16):
        if table is not None:
            result += table[arr[i] % len(table)]
        else:
            if r <= i and len(result)<8:
                idx = arr[i] % len(encscans)
                scan_char_idx = encscans[idx]
                if scan_char_idx < len(scanCodes):
                    result += scanCodes[scan_char_idx]
    return result

def calculateE7A8(block: List[int], klass) -> str:
    table = "Q92G0drk9y63r5DG1hLqJGW1EnRk[QxrFMNZ328I6myLr4MsPNeZR2z72czpzUJBGXbaIjkZ"
    encoded_32 = klass.encode(block)
    res_bytes = intArrayToByte(encoded_32)
    digest = hashlib.sha256(bytes(res_bytes)).digest()  # 32 bytes
    out_str=""
    for i in range(16):
        idx=(digest[i+16]+digest[i])%len(table)
        out_str+=table[idx]
    return out_str

def keygenDell(serial: str, tag: str, type_: int) -> List[str]:
    if tag == DellTag.TagA95B:
        fullSerial = serial + DellTag.Tag595B
    else:
        fullSerial = serial + tag

    fullSerialArray = [ord(c) for c in fullSerial]

    if tag == DellTag.TagE7A8:
        encBlock = byteArrayToInt(fullSerialArray)
        for i in range(16):
            if i>= len(encBlock):
                encBlock.append(0)
        out_str1 = calculateE7A8(encBlock, TagE7A8Encoder)
        out_str2 = calculateE7A8(encBlock, TagE7A8EncoderSecond)
        results = []
        if out_str1:
            results.append(out_str1)
        if out_str2:
            results.append(out_str2)
        return results

    # otherwise => normal suffix approach
    suffix = calculateSuffix(fullSerialArray, tag, type_)
    fullSerialArray += suffix
    cnt=23
    if len(fullSerialArray)<=cnt:
        fullSerialArray+=[0]*(cnt-len(fullSerialArray)+1)
    fullSerialArray[cnt]=0x80
    encBlock=byteArrayToInt(fullSerialArray)
    for i in range(16):
        if i>= len(encBlock):
            encBlock.append(0)
    encBlock[14]=(cnt<<3)
    decodedBytes=intArrayToByte(blockEncode(encBlock, tag))
    outputResult=resultToString(decodedBytes, tag)
    return [outputResult] if outputResult else []

def checkDellTag(tag: str) -> bool:
    tag=tag.upper()
    valid_tags = {
        DellTag.Tag595B, DellTag.TagD35B, DellTag.Tag2A7B, DellTag.TagA95B,
        DellTag.Tag1D3B, DellTag.Tag1F66, DellTag.Tag6FF1, DellTag.Tag1F5A,
        DellTag.TagBF97, DellTag.TagE7A8
    }
    return (tag in valid_tags)

def dellSolverFun(password: str) -> List[str]:
    if len(password)!=11:
        return []
    serial_part = password[:7].upper()
    tag_part = password[7:].upper()
    if not checkDellTag(tag_part):
        return []
    return keygenDell(serial_part, tag_part, SuffixType.ServiceTag)

def dellSolverValidator(password: str) -> bool:
    return (len(password)==11 and checkDellTag(password[7:]))

################################################################################
# PART 3: Combined GUI with Tabbed Interface
################################################################################

class BiosUnlockerTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # File Selection
        tk.Label(self.frame, text="Select BIOS File:", font=("Arial", 10, "bold")).pack(pady=5)
        file_frame = tk.Frame(self.frame)
        file_frame.pack(pady=5)

        self.entry = tk.Entry(file_frame, width=50, borderwidth=0, font=("Arial", 9))
        self.entry.pack(side=tk.LEFT, padx=5)

        browse_button = tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#4682B4", fg="white")
        browse_button.pack(side=tk.RIGHT, padx=5)

        # Patch Button (white background)
        self.patch_button = tk.Button(self.frame, text="Patch BIOS", command=self.patch_bios,
                                    bg="white",  # White background
                                    fg="black",  # Black text for contrast
                                    font=("Arial", 10, "bold"), 
                                    padx=10, 
                                    state=tk.DISABLED,
                                    borderwidth=1,  # Minimal border
                                    relief="solid",  # Solid border style
                                    activebackground="#E0E0E0")  # Light gray when clicked
        self.patch_button.pack(pady=10)

        # Log Display
        log_frame = tk.Frame(self.frame, bg="#36454F")
        log_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        tk.Label(log_frame, text="Patching Log:", bg="#36454F", fg="white", anchor="w").pack(fill=tk.X)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=18, state=tk.DISABLED, bg="black", fg="#00FF00", font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # About Label
        about_text = """ English Version of the Rex98-8FC8-Patcher
Based on the original tool by Rex98 & Techshack Cebu
Use with caution: Improper BIOS modification can damage your system."""
        about_label = tk.Label(self.frame, text=about_text, fg="#CCCCCC", font=("Arial", 8), justify=tk.LEFT)
        about_label.pack(pady=5)

        self.log_message("Welcome to Dell-8FC8-BIOS-UNLOCKER")
        self.log_message("This tool helps unlock Dell BIOS by patching specific patterns")
        self.log_message("Please select a BIOS file to begin")
        self.log_message("For password generation, use the Password Generator tab")

    def log_message(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.parent.update()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("BIOS Files", "*.bin *.rom *.fd *.bio"),
            ("All Files", "*.*")
        ])
        if file_path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, file_path)
            self.log_message(f"Selected file: {file_path}")
            self.patch_button.config(text="Patch BIOS", state=tk.NORMAL)

    def patch_bios(self):
        file_path = self.entry.get()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid BIOS file first!")
            return
            
        self.log_message("Starting BIOS patching process...")

        try:
            with open(file_path, "rb") as f:
                bios_data = bytearray(f.read())

            file_name = os.path.basename(file_path)
            file_size = len(bios_data)
            self.log_message(f"Loaded BIOS file: {file_name} (Size: {file_size} bytes)")

            # Look for Intel signature
            intel_signature = convert_hex_to_bytes("5AA5F00F03")
            self.log_message("Searching for Intel signature...")
            intel_offset = find_intel_signature(bios_data, intel_signature)

            if intel_offset >= 0:
                self.log_message(f"Intel signature found at offset 0x{intel_offset:X}")
            else:
                self.log_message("Intel signature not found")
                messagebox.showerror("Error", "Intel signature not found. This may not be a valid BIOS file.")
                return

            # First pattern
            self.log_message("Checking for first pattern...")
            first_pattern = r"^00FCAA[0-9A-F]{2,4}000000[0-9A-F]{2,}.*$"
            first_replace_bytes = convert_hex_to_bytes("00FC00")
            
            first_offsets = find_pattern_matches(bios_data, first_pattern)
            
            for offset in first_offsets:
                self.log_message(f"Pattern found at offset 0x{offset:X} and replaced.")
                bios_data[offset:offset+6] = first_replace_bytes + bytes([0] * (6 - len(first_replace_bytes)))

            # Second pattern
            self.log_message("Almost done! Checking second pattern...")
            second_pattern = r"^00FDAA[0-9A-F]{2,4}000000[0-9A-F]{2,}.*$"
            second_replace_bytes = convert_hex_to_bytes("00FD00")
            
            second_offsets = find_pattern_matches(bios_data, second_pattern)
            
            for offset in second_offsets:
                self.log_message(f"Pattern found at offset 0x{offset:X} and replaced.")
                bios_data[offset:offset+6] = second_replace_bytes + bytes([0] * (6 - len(second_replace_bytes)))

            if first_offsets or second_offsets:
                patched_file_path = os.path.join(os.path.dirname(file_path), f"patched_{file_name}")
                with open(patched_file_path, "wb") as f:
                    f.write(bios_data)
                self.log_message(f"Patched and saved as patched_{file_name}")
                self.patch_button.config(text="Completed!", state=tk.DISABLED)
                messagebox.showinfo("Success", f"BIOS patched successfully!\nSaved as {patched_file_path}")

                # Updated custom message with new instruction
                self.log_message("Use your BIOS Programmer to flash the patched bin file to your device.")
                self.log_message("Reboot the device.. A warning will come up: 'The Service Tag has not been programmed...'.")
                self.log_message("After inputting the Service Tag, the device will reboot again and you should be able to boot to the Windows OS.")
                self.log_message("For other BIOS password needs, use the Password Generator tab.")

            else:
                self.log_message("Patching failed: No patterns found")
                messagebox.showwarning("Warning", "No matching patterns found. Patch unsuccessful.")

        except Exception as e:
            self.log_message(f"Error during patching: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

class PasswordGeneratorTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        frame = tk.Frame(self.frame, padx=10, pady=10)
        frame.pack(expand=True)

        # Title
        title_label = tk.Label(frame, text="Dell BIOS Password Generator", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)

        # Instructions
        instructions = tk.Label(frame, text="Enter 7-character Service Tag followed by 4-character Tag suffix\n(Example: 1A2B3C4595B)", justify=tk.CENTER)
        instructions.pack(pady=5)

        # Input field
        input_frame = tk.Frame(frame)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Service Tag + Suffix:").pack(side=tk.LEFT)
        self.user_input = tk.Entry(input_frame, width=20)
        self.user_input.pack(side=tk.LEFT, padx=5)

        # Available tags
        tags_frame = tk.Frame(frame)
        tags_frame.pack(pady=5)
        
        tk.Label(tags_frame, text="Common Tags:").pack(side=tk.LEFT)
        tk.Label(tags_frame, text="595B, D35B, 2A7B, 1D3B, 1F66, 6FF1, 1F5A, BF97, E7A8", fg="blue").pack(side=tk.LEFT, padx=5)

        # Button
        compute_button = tk.Button(frame, text="Compute Password", command=self.compute_password, bg="#4682B4", fg="white")
        compute_button.pack(pady=10)

        # Result display
        result_frame = tk.Frame(frame)
        result_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(result_frame, text="Password:").pack(side=tk.LEFT)
        self.result_display = tk.Entry(result_frame, width=30, state="readonly")
        self.result_display.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Note
        note_text = "Note: For 8FC8 suffixes, use the 'Patch BIOS' tool instead."
        note_label = tk.Label(frame, text=note_text, fg="red", font=("Arial", 9))
        note_label.pack(pady=5)

        # Additional information
        info_frame = tk.Frame(frame)
        info_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        info_text = """Instructions:
1. Enter your 7-character Dell Service Tag followed by a 4-character tag suffix
2. Click "Compute Password" to generate the BIOS master password
3. For E7A8 tags, you may receive two possible passwords - try both

Warning: Use at your own risk. Incorrect BIOS passwords can lock your system."""
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9))
        info_label.pack(anchor=tk.W)

    def compute_password(self):
        text = self.user_input.get().strip()
        
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(0, tk.END)
        
        if dellSolverValidator(text):
            results = dellSolverFun(text)
            if results:
                self.result_display.insert(0, ", ".join(results))
            else:
                self.result_display.insert(0, "No valid password found for this input.")
        else:
            self.result_display.insert(0, "Invalid input format. Use 7-char tag + 4-char suffix.")
        
        self.result_display.config(state="readonly")

class DellToolsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dell BIOS Tools.V2")
        self.root.geometry("650x580")
        self.root.configure(bg="#36454F")

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.unlocker_tab = BiosUnlockerTab(self.notebook)
        self.password_tab = PasswordGeneratorTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.unlocker_tab.frame, text="BIOS Unlocker")
        self.notebook.add(self.password_tab.frame, text="Password Generator")

def main():
    root = tk.Tk()
    app = DellToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()