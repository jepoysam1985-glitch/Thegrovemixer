import re, shutil, pathlib, os, sys
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

# Ang package folder ay DAPAT tugma sa appId (capacitor.config.json). Dati, 'com/groovemixer/app' ang
# nilalagyan kaya nadodoble ang MainActivity at hindi nakarehistro ang TcpSocket sa APK.
import json
_app_id = json.load(open('capacitor.config.json', encoding='utf-8'))['appId']
pkg_dir = root / 'java' / pathlib.Path(*_app_id.split('.'))
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

# ---- Mas malinaw na GO LIVE: hanapin ang TcpSocket sa iba't ibang paraan at ipakita kung ano ang nakarehistro ----
# Inaayos ang www/index.html bago ang `cap sync`. Ligtas patakbuhin ulit; kapag iba ang code, babala lang (hindi titigil ang build).
_www = 'www/index.html'
if os.path.exists(_www):
    _s = open(_www, encoding='utf-8').read()
    if 'function nativePlugins()' in _s:
        print('index.html: naka-patch na ang getTcp')
    else:
        _a = _s.find("let _tcp = null;\nfunction getTcp() {")
        _b = _s.find("const Tcp = new Proxy({}")
        _c = _s.find("  if (!getTcp()) { setStatus('No Capacitor/TcpSocket found.")
        _d = _s.find("  if (!window.lamejs)", _c) if _c != -1 else -1
        if _a != -1 and _b > _a and _c > _b and _d > _c:
            NEW_GET = '''let _tcp = null;
function nativePlugins() {   // pangalan ng mga native plugin na nakarehistro sa APK (null = hindi malaman)
  try { const h = window.Capacitor && Capacitor.PluginHeaders; if (Array.isArray(h)) return h.map((x) => x.name); } catch (_e) {}
  return null;
}
function getTcp() {
  if (_tcp) return _tcp;
  const C = window.Capacitor;
  if (!C) return null;
  let t = null;
  try { if (C.Plugins && C.Plugins.TcpSocket) t = C.Plugins.TcpSocket; } catch (_e) {}
  if (!t && typeof C.registerPlugin === 'function') { try { t = C.registerPlugin('TcpSocket'); } catch (_e) {} }
  if (!t && typeof C.nativePromise === 'function') t = new Proxy({}, { get: (_, m) => (m === 'then' ? undefined : (o) => C.nativePromise('TcpSocket', m, o || {})) });
  return (_tcp = t);
}
'''
            NEW_CHK = '''  { const np = nativePlugins(), isNative = !!(window.Capacitor && Capacitor.isNativePlatform && Capacitor.isNativePlatform());
    if (!window.Capacitor) { setStatus('Not running inside the APK app (no Capacitor). Install the APK, do not open in a browser.', false); return; }
    if (!getTcp() || (np && !np.includes('TcpSocket'))) {
      setStatus('APK is missing the TcpSocket plugin' + (isNative ? '' : ' (not native)') + (np ? ' - found: ' + (np.join(', ') || 'none') : '') + '. Rebuild the APK from the latest GitHub files.', false); return; } }
'''
            _s = _s[:_a] + NEW_GET + _s[_b:_c] + NEW_CHK + _s[_d:]
            open(_www, 'w', encoding='utf-8').write(_s)
            print('index.html: getTcp at diagnostics ay napalitan')
        else:
            print('::warning::Hindi nahanap ang getTcp sa www/index.html - hindi napalitan (hindi ito dahilan para huminto)')

# ---- PERFORMANCE (Snapdragon 680 / mid-range phone): bawasan ang bigat ng LED ring at spectrum para hindi mag-lag ----
# Sinukat sa 4x na mabagal na CPU habang tumutugtog ang 2 deck: 44 -> 56 fps at 85% -> 64% ang gamit ng main thread.
if os.path.exists(_www):
    _s = open(_www, encoding='utf-8').read()
    if '/*gm-perf*/' in _s:
        print('perf: naka-patch na')
    else:
        _perf = [
            # spectrum / waveform canvas: ~15fps at mas maliit na resolution (1x)
            ("if (!window.__scr && (now || 0) - (draw._t || 0) < 38) return;", "if (!window.__scr && (now || 0) - (draw._t || 0) < 66) return;"),
            ("const dpr = Math.min(window.devicePixelRatio || 1, 1.5);", "const dpr = 1;"),
        ]
        _miss = [a[:50] for a, b in _perf if _s.count(a) != 1]
        if _miss:
            print('::warning::perf: hindi nahanap ang mga linya, hindi ginalaw:', _miss)
        else:
            for a, b in _perf:
                _s = _s.replace(a, b)
            open(_www, 'w', encoding='utf-8').write(_s)
            print('perf: naka-patch OK (LED ring, spectrum, canvas resolution)')

# ---- Siguraduhing nakarehistro ang TcpSocket (at ForegroundService) sa MainActivity ----
# Dito tinatawag ang ensure_tcp.py para gumana kahit alin ang workflow na tumatakbo sa GitHub.
import os, runpy, sys
for _cand in ('ensure_tcp.py', 'scripts/ensure_tcp.py'):
    if os.path.exists(_cand):
        runpy.run_path(_cand, run_name='__main__')
        break
else:
    sys.exit('::error::Walang ensure_tcp.py - i-upload ito sa pinakaibabaw ng repo')
