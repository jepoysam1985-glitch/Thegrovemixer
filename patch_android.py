import re, shutil, pathlib
root = pathlib.Path('android/app/src/main')
mf = root / 'AndroidManifest.xml'
x = mf.read_text(encoding='utf-8')

perms = """
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
"""
for name in re.findall(r'android:name="(android\.permission\.[A-Z_]+)"', perms):
    x = re.sub(r'\s*<uses-permission android:name="%s"\s*/>' % re.escape(name), '', x)

if 'AndroidForegroundService' not in x:
    x = x.replace('<application', perms + '\n    <application', 1)
    x = x.replace('<application', '<application android:usesCleartextTraffic="true"', 1)
    svc = """
        <service android:name="io.capawesome.capacitorjs.plugins.foregroundservice.AndroidForegroundService"
            android:foregroundServiceType="microphone|mediaPlayback" android:exported="false" />
        <receiver android:name="io.capawesome.capacitorjs.plugins.foregroundservice.NotificationActionBroadcastReceiver"
            android:exported="false" />
    """
    x = x.replace('</application>', svc + '\n    </application>', 1)
mf.write_text(x, encoding='utf-8')

pkg_dir = root / 'java' / 'com' / 'groovemixer' / 'app'
pkg_dir.mkdir(parents=True, exist_ok=True)
for f in pathlib.Path('native/java').glob('*.java'):
    shutil.copy(f, pkg_dir / f.name)

(root / 'res' / 'drawable').mkdir(parents=True, exist_ok=True)
shutil.copy('native/res/drawable/ic_stat_icon.xml', root / 'res' / 'drawable' / 'ic_stat_icon.xml')

sv = root / 'res' / 'values' / 'strings.xml'
if sv.exists():
    s = sv.read_text(encoding='utf-8')
    s = re.sub(r'(<string name="app_name">)[^<]*(</string>)', r'\1THE GROOVE MIXER\2', s)
    s = re.sub(r'(<string name="title_activity_main">)[^<]*(</string>)', r'\1THE GROOVE MIXER\2', s)
    sv.write_text(s, encoding='utf-8')

# FULL SCREEN theme: itago ang status/navigation bar at sakupin ang notch (landscape)
st = root / 'res' / 'values' / 'styles.xml'
if st.exists():
    t = st.read_text(encoding='utf-8')
    if 'windowFullscreen' not in t:
        items = ('\n        <item name="android:windowFullscreen">true</item>'
                 '\n        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>'
                 '\n        <item name="android:windowBackground">@android:color/black</item>'
                 '\n        <item name="android:statusBarColor">@android:color/transparent</item>'
                 '\n        <item name="android:navigationBarColor">@android:color/transparent</item>')
        t = re.sub(r'(<style name="AppTheme[^"]*"[^>]*>)', lambda m: m.group(1) + items, t)
        st.write_text(t, encoding='utf-8')
        print('styles.xml: fullscreen theme added')
print('Android project patched OK')
