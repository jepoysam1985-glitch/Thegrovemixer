# Android 15+ (targetSdk 35) ay pinipilit ang edge-to-edge: huwag hayaang matakpan ng status bar ang app.
import os, re

p = 'android/app/src/main/res/values/styles.xml'
if not os.path.exists(p):
    print('edge: walang styles.xml, skip')
    raise SystemExit(0)
s = open(p, encoding='utf-8').read()
item = '<item name="android:windowOptOutEdgeToEdgeEnforcement">true</item>'
if 'windowOptOutEdgeToEdgeEnforcement' not in s:
    s = re.sub(r'(<style name="AppTheme[^"]*"[^>]*>)', lambda m: m.group(1) + '\n        ' + item, s)
    open(p, 'w', encoding='utf-8').write(s)
print(s)
