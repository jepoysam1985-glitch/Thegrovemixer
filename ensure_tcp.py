#!/usr/bin/env python3
"""Sinisiguro na nakarehistro ang TcpSocket plugin sa Android project. Ligtas patakbuhin kahit ilang beses."""
import json, os, re, shutil, glob, sys

cfg = json.load(open('capacitor.config.json', encoding='utf-8'))
app_id = cfg['appId']
jdir = os.path.join('android/app/src/main/java', *app_id.split('.'))
os.makedirs(jdir, exist_ok=True)

# 1) hanapin ang TcpSocketPlugin.java (kahit saang lugar ng repo)
src = None
for c in ['native/java/TcpSocketPlugin.java', 'TcpSocketPlugin.java'] + glob.glob('**/TcpSocketPlugin.java', recursive=True):
    if os.path.isfile(c):
        src = c
        break
if not src:
    sys.exit('::error::Walang TcpSocketPlugin.java sa repo')

dst = os.path.join(jdir, 'TcpSocketPlugin.java')
code = open(src, encoding='utf-8').read()
code = re.sub(r'^\s*package\s+[\w.]+\s*;', 'package %s;' % app_id, code, count=1, flags=re.M)
if 'package ' not in code:
    code = 'package %s;\n' % app_id + code
open(dst, 'w', encoding='utf-8').write(code)
print('Plugin copied ->', dst)

# 2) MainActivity: siguraduhing may registerPlugin bago ang super.onCreate
ma = os.path.join(jdir, 'MainActivity.java')
if not os.path.isfile(ma):
    found = glob.glob('android/app/src/main/java/**/MainActivity.java', recursive=True)
    if not found:
        sys.exit('::error::Walang MainActivity.java sa android project')
    ma = found[0]
s = open(ma, encoding='utf-8').read()
s = re.sub(r'^\s*package\s+[\w.]+\s*;', 'package %s;' % app_id, s, count=1, flags=re.M)
if 'registerPlugin(TcpSocketPlugin.class)' not in s:
    if 'super.onCreate' in s:
        s = re.sub(r'(\n\s*)super\.onCreate\(', r'\1registerPlugin(TcpSocketPlugin.class);\1super.onCreate(', s, count=1)
    else:
        if 'import android.os.Bundle;' not in s:
            s = re.sub(r'(package [^;]+;)', r'\1\nimport android.os.Bundle;', s, count=1)
        s = re.sub(r'(class MainActivity extends BridgeActivity\s*\{)',
                   r'\1\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n        registerPlugin(TcpSocketPlugin.class);\n        super.onCreate(savedInstanceState);\n    }', s, count=1)
    open(ma, 'w', encoding='utf-8').write(s)
    print('MainActivity patched:', ma)
else:
    print('MainActivity already registers TcpSocketPlugin:', ma)
print('--- MainActivity.java ---')
print(open(ma, encoding='utf-8').read())
