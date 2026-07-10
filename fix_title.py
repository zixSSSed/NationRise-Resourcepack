# -*- coding: utf-8 -*-
import re
PATH = r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\Townlands\src\main\java\dev\townlands\ScoreboardService.java"
SECTION = "§"   # §
LOGO = chr(0xE010)
src = open(PATH, encoding="utf-8").read()
canonical = 'legacy("' + SECTION + 'f' + LOGO + '")'
pattern = re.compile(r'legacy\("' + SECTION + r'f[^"]*"\)')
new, n = pattern.subn(canonical, src, count=1)
open(PATH, "w", encoding="utf-8").write(new)
chk = open(PATH, encoding="utf-8").read()
m = re.search(r'legacy\("' + SECTION + r'f([^"]*)"\)', chk)
print("replacements:", n)
print("title arg after section+f codepoints:", [hex(ord(c)) for c in m.group(1)] if m else "NONE")
