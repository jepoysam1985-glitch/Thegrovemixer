#!/usr/bin/env python3
"""Sinisiguro na may ISANG MainActivity at ISANG TcpSocketPlugin, at nakarehistro ang TcpSocket. Ligtas patakbuhin ulit."""
import json, os, re, glob, sys

cfg = json.load(open('capacitor.config.json', encoding='utf-8'))
app_id = cfg['appId']
root = 'android/app/src/main/java'
jdir = os.path.join(root, *app_id.split('.'))
os.makedirs(jdir, exist_ok=True)
PKG = re.compile(r'^\s*package\s+[\w.]+\s*;', re.M)

def rd(f): return open(f, encoding='utf-8').read()
def wr(f, t): open(f, 'w', encoding='utf-8').write(t)

# ---------- TcpSocketPlugin: burahin ang lahat ng kopya, isang malinis na kopya lang ----------
src = None
for c in ['native/java/TcpSocketPlugin.java', 'TcpSocketPlugin.java']:
    if os.path.isfile(c):
        src = c
        break
if not src:
    sys.exit('::error::Walang TcpSocketPlugin.java sa repo')
code = rd(src)
code = PKG.sub('package %s;' % app_id, code, count=1) if PKG.search(code) else 'package %s;\n' % app_id + code
for f in glob.glob(root + '/**/TcpSocketPlugin.java', recursive=True):
    os.remove(f)
dst = os.path.join(jdir, 'TcpSocketPlugin.java')
wr(dst, code)
print('Plugin ->', dst)

# ---------- MainActivity: itira ang pinakakumpleto, burahin ang doble ----------
files = glob.glob(root + '/**/MainActivity.java', recursive=True)
if not files:
    sys.exit('::error::Walang MainActivity.java sa android project')
files.sort(key=lambda f: (rd(f).count('registerPlugin'), len(rd(f))), reverse=True)
keep = files[0]
for f in files[1:]:
    print('Binubura ang doble:', f)
    os.remove(f)

s = rd(keep)
s = PKG.sub('package %s;' % app_id, s, count=1)
if 'registerPlugin(TcpSocketPlugin.class)' not in s:
    if 'super.onCreate' in s:
        s = re.sub(r'(\n\s*)super\.onCreate\(', r'\1registerPlugin(TcpSocketPlugin.class);\1super.onCreate(', s, count=1)
    else:
        if 'import android.os.Bundle;' not in s:
            s = re.sub(r'(package [^;]+;)', r'\1\nimport android.os.Bundle;', s, count=1)
        s = re.sub(r'(class MainActivity extends BridgeActivity\s*\{\s*\}?)',
                   'class MainActivity extends BridgeActivity {\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n        registerPlugin(TcpSocketPlugin.class);\n        super.onCreate(savedInstanceState);\n    }\n}', s, count=1)
wr(keep, s)
print('--- MainActivity:', keep, '---')
print(s)
