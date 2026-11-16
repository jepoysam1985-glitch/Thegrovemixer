#!/usr/bin/env python3
"""
Ginagawang TUGMA ang native Android sa index.html:
  - TcpSocket        : connect({host,port}) / write({data:base64}) / read({timeoutMs}) -> {text} / close()
  - ForegroundService: requestPermissions() / startForegroundService({id,title,body,smallIcon}) / stopForegroundService()
Sinisiguro rin na: iisa lang ang MainActivity, nakarehistro ang dalawang plugin, at kumpleto ang manifest.
Ligtas patakbuhin kahit ilang beses. Patakbuhin pagkatapos ng `cap add android` at ng patch_android.py.
"""
import json, os, re, glob, sys

cfg = json.load(open('capacitor.config.json', encoding='utf-8'))
APP = cfg['appId']
SRC = 'android/app/src'
JDIR = os.path.join(SRC, 'main', 'java', *APP.split('.'))
os.makedirs(JDIR, exist_ok=True)
PKG_RE = re.compile(r'^\s*package\s+[\w.]+\s*;', re.M)

def rd(f): return open(f, encoding='utf-8').read()
def wr(f, t):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(t)

TCP = r'''package __PKG__;

import android.util.Base64;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** TCP socket para sa GO LIVE (Icecast / Shoutcast). Tugma sa index.html: connect, write, read, close. */
@CapacitorPlugin(name = "TcpSocket")
public class TcpSocketPlugin extends Plugin {
    private volatile Socket socket;
    private volatile InputStream in;
    private volatile OutputStream out;
    private final ExecutorService io = Executors.newSingleThreadExecutor();

    @PluginMethod
    public void connect(final PluginCall call) {
        final String host = call.getString("host");
        final int port = call.getInt("port", 0);
        io.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    closeQuiet();
                    Socket s = new Socket();
                    s.setTcpNoDelay(true);
                    s.setKeepAlive(true);
                    s.connect(new InetSocketAddress(host, port), 10000);
                    in = s.getInputStream();
                    out = s.getOutputStream();
                    socket = s;
                    call.resolve();
                } catch (Exception e) {
                    closeQuiet();
                    call.reject("Connect failed: " + e.getMessage());
                }
            }
        });
    }

    @PluginMethod
    public void write(final PluginCall call) {
        final String data = call.getString("data", "");
        io.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    OutputStream os = out;
                    if (os == null) { call.reject("Not connected"); return; }
                    os.write(Base64.decode(data, Base64.DEFAULT));
                    os.flush();
                    call.resolve();
                } catch (Exception e) {
                    call.reject("Write failed: " + e.getMessage());
                }
            }
        });
    }

    @PluginMethod
    public void read(final PluginCall call) {
        final int timeout = call.getInt("timeoutMs", 5000);
        io.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    Socket s = socket;
                    InputStream is = in;
                    if (s == null || is == null) { call.reject("Not connected"); return; }
                    s.setSoTimeout(timeout);
                    byte[] buf = new byte[4096];
                    int n;
                    try { n = is.read(buf); } catch (SocketTimeoutException t) { n = 0; }
                    JSObject r = new JSObject();
                    r.put("text", n > 0 ? new String(buf, 0, n, StandardCharsets.ISO_8859_1) : "");
                    call.resolve(r);
                } catch (Exception e) {
                    call.reject("Read failed: " + e.getMessage());
                }
            }
        });
    }

    @PluginMethod
    public void close(PluginCall call) {
        closeQuiet();   // diretso, para maputol kahit may nakabinbing write
        call.resolve();
    }

    private void closeQuiet() {
        Socket s = socket;
        socket = null; in = null; out = null;
        try { if (s != null) s.close(); } catch (Exception ignored) {}
    }

    @Override
    protected void handleOnDestroy() {
        closeQuiet();
        io.shutdownNow();
    }
}
'''

FGS_PLUGIN = r'''package __PKG__;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/** ON AIR sa background. Tugma sa index.html: requestPermissions, startForegroundService, stopForegroundService. */
@CapacitorPlugin(name = "ForegroundService")
public class ForegroundServicePlugin extends Plugin {

    @Override
    @PluginMethod
    public void requestPermissions(PluginCall call) {
        try {
            if (Build.VERSION.SDK_INT >= 33 && getActivity() != null
                    && ContextCompat.checkSelfPermission(getContext(), "android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(getActivity(), new String[]{"android.permission.POST_NOTIFICATIONS"}, 4243);
            }
        } catch (Exception ignored) {}
        JSObject r = new JSObject();
        r.put("display", "granted");
        call.resolve(r);
    }

    @PluginMethod
    public void startForegroundService(PluginCall call) {
        try {
            int id = call.getInt("id", 4242);
            Intent i = new Intent(getContext(), GrooveService.class);
            i.putExtra("id", id);
            i.putExtra("title", call.getString("title", "THE GROOVE MIXER - ON AIR"));
            i.putExtra("body", call.getString("body", "Live ka pa."));
            i.putExtra("smallIcon", call.getString("smallIcon", "ic_stat_icon"));
            ContextCompat.startForegroundService(getContext(), i);
            call.resolve();
        } catch (Exception e) {
            call.reject("Foreground service failed: " + e.getMessage());
        }
    }

    @PluginMethod
    public void stopForegroundService(PluginCall call) {
        try {
            getContext().stopService(new Intent(getContext(), GrooveService.class));
        } catch (Exception ignored) {}
        call.resolve();
    }
}
'''

SERVICE = r'''package __PKG__;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

/** Foreground service na nagpapanatiling buhay ang tugtog at stream habang ON AIR. */
public class GrooveService extends Service {
    private static final String CHANNEL = "groove_on_air";
    private PowerManager.WakeLock wl;

    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        int id = 4242;
        String title = "THE GROOVE MIXER - ON AIR";
        String body = "Live ka pa.";
        String icon = "ic_stat_icon";
        if (intent != null) {
            id = intent.getIntExtra("id", id);
            if (intent.getStringExtra("title") != null) title = intent.getStringExtra("title");
            if (intent.getStringExtra("body") != null) body = intent.getStringExtra("body");
            if (intent.getStringExtra("smallIcon") != null) icon = intent.getStringExtra("smallIcon");
        }
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm != null && nm.getNotificationChannel(CHANNEL) == null) {
                nm.createNotificationChannel(new NotificationChannel(CHANNEL, "On Air", NotificationManager.IMPORTANCE_LOW));
            }
        }
        int small = getResources().getIdentifier(icon, "drawable", getPackageName());
        if (small == 0) small = getApplicationInfo().icon;
        if (small == 0) small = android.R.drawable.ic_media_play;

        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int pf = PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open, pf);

        Notification n = new NotificationCompat.Builder(this, CHANNEL)
                .setContentTitle(title)
                .setContentText(body)
                .setSmallIcon(small)
                .setContentIntent(pi)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setCategory(NotificationCompat.CATEGORY_SERVICE)
                .build();

        boolean started = false;
        if (Build.VERSION.SDK_INT >= 30) {
            try {
                int type = ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK;
                if (ContextCompat.checkSelfPermission(this, "android.permission.RECORD_AUDIO") == PackageManager.PERMISSION_GRANTED) {
                    type |= ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE;
                }
                startForeground(id, n, type);
                started = true;
            } catch (Exception e) {
                started = false;
            }
            if (!started) {
                try {
                    startForeground(id, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
                    started = true;
                } catch (Exception e) {
                    started = false;
                }
            }
        } else {
            try {
                startForeground(id, n);
                started = true;
            } catch (Exception e) {
                started = false;
            }
        }
        if (!started) {
            stopSelf();
            return START_NOT_STICKY;
        }

        if (wl == null) {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            if (pm != null) {
                wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "groovemixer:onair");
                wl.setReferenceCounted(false);
            }
        }
        try {
            if (wl != null && !wl.isHeld()) wl.acquire(6 * 60 * 60 * 1000L);
        } catch (Exception ignored) {}
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        try { stopForeground(true); } catch (Exception ignored) {}
        try { if (wl != null && wl.isHeld()) wl.release(); } catch (Exception ignored) {}
        super.onDestroy();
    }
}
'''

def fill(t): return t.replace('__PKG__', APP)

def plugin_files(js):
    out = []
    for f in glob.glob(SRC + '/**/*.java', recursive=True):
        if re.search(r'@CapacitorPlugin\s*\(\s*name\s*=\s*"%s"' % re.escape(js), rd(f)):
            out.append(f)
    return out

def class_of(f):
    m = re.search(r'class\s+(\w+)\s+extends\s+Plugin', rd(f))
    return m.group(1) if m else None

print('=== Nakita bago mag-ayos ===')
for pat in ('MainActivity.*', 'TcpSocketPlugin.*', 'ForegroundService*.*', 'GrooveService.*'):
    for f in sorted(glob.glob(SRC + '/**/' + pat, recursive=True)):
        print(' ', f)
print('============================')

classes = []

# ---------- TcpSocket: akin ang pangalan na ito; burahin ang lahat ng kopya, isa lang ang titira ----------
for f in set(plugin_files('TcpSocket') + glob.glob(SRC + '/**/TcpSocketPlugin.java', recursive=True)):
    os.remove(f)
wr(os.path.join(JDIR, 'TcpSocketPlugin.java'), fill(TCP))
classes.append('TcpSocketPlugin')
print('OK TcpSocketPlugin ->', JDIR)

# ---------- ForegroundService ----------
ours = os.path.join(JDIR, 'ForegroundServicePlugin.java')
others = [f for f in plugin_files('ForegroundService') if os.path.basename(f) != 'ForegroundServicePlugin.java']
need_service = True
if others:
    print('May ForegroundService na sa project, ginagamit ito:', others)
    for f in others:
        c = class_of(f)
        if c: classes.append(c)
    need_service = False
else:
    for f in glob.glob(SRC + '/**/ForegroundServicePlugin.java', recursive=True):
        os.remove(f)
    wr(ours, fill(FGS_PLUGIN))
    wr(os.path.join(JDIR, 'GrooveService.java'), fill(SERVICE))
    classes.append('ForegroundServicePlugin')
    print('OK ForegroundServicePlugin + GrooveService ->', JDIR)

# ---------- MainActivity: isa lang ----------
files = glob.glob(SRC + '/**/MainActivity.java', recursive=True) + glob.glob(SRC + '/**/MainActivity.kt', recursive=True)
if not files:
    sys.exit('::error::Walang MainActivity sa android project')
files.sort(key=lambda f: (rd(f).count('registerPlugin'), len(rd(f))), reverse=True)
keep = files[0]
for f in files[1:]:
    print('Binubura ang doble:', f)
    os.remove(f)
if keep.endswith('.kt'):
    sys.exit('::error::Kotlin ang MainActivity: ' + keep)

s = rd(keep)
s = PKG_RE.sub('package %s;' % APP, s, count=1)
missing = [c for c in classes if ('registerPlugin(%s.class)' % c) not in s]
if missing:
    if 'import android.os.Bundle;' not in s:
        s = re.sub(r'(package [^;]+;)', r'\1\n\nimport android.os.Bundle;', s, count=1)
    if 'super.onCreate' in s:
        def ins(m):
            ind = m.group(1)
            return ''.join('%sregisterPlugin(%s.class);' % (ind, c) for c in missing) + ind + 'super.onCreate('
        s = re.sub(r'(\n[ \t]*)super\.onCreate\(', ins, s, count=1)
    else:
        regs = ''.join('        registerPlugin(%s.class);\n' % c for c in missing)
        method = ('\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n' + regs +
                  '        super.onCreate(savedInstanceState);\n    }\n')
        s, n = re.subn(r'(class\s+MainActivity\s+extends\s+BridgeActivity\s*\{)', lambda m: m.group(1) + method, s, count=1)
        if not n:
            sys.exit('::error::Hindi maintindihan ang MainActivity: ' + keep)
wr(keep, s)
print('--- MainActivity:', keep, '---')
print(s)

# ---------- Manifest ----------
mf = os.path.join(SRC, 'main', 'AndroidManifest.xml')
m = rd(mf)
perms = ['INTERNET', 'RECORD_AUDIO', 'MODIFY_AUDIO_SETTINGS', 'WAKE_LOCK', 'FOREGROUND_SERVICE',
         'FOREGROUND_SERVICE_MEDIA_PLAYBACK', 'FOREGROUND_SERVICE_MICROPHONE', 'POST_NOTIFICATIONS']
add = ''.join('    <uses-permission android:name="android.permission.%s" />\n' % p
              for p in perms if ('android.permission.%s"' % p) not in m)
if add:
    m = m.replace('</manifest>', add + '</manifest>', 1)
if need_service and '.GrooveService' not in m:
    m = m.replace('</application>',
                  '        <service android:name=".GrooveService" android:exported="false" '
                  'android:foregroundServiceType="mediaPlayback|microphone" />\n    </application>', 1)
wr(mf, m)
print('--- Manifest (permissions / service) ---')
for line in m.splitlines():
    if 'permission' in line or 'service' in line.lower():
        print(line.strip())
print('=== TAPOS: plugins na nakarehistro =', classes)
