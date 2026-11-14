# Capacitor (walang bundler): walang Capacitor.registerPlugin, kaya gamitin ang Capacitor.Plugins.<Name>
p = 'www/index.html'
s = open(p, encoding='utf-8').read()

pairs = [
    ("window.Capacitor && Capacitor.registerPlugin ? Capacitor.registerPlugin('TcpSocket') : null",
     "window.Capacitor ? (Capacitor.registerPlugin ? Capacitor.registerPlugin('TcpSocket') : ((Capacitor.Plugins && Capacitor.Plugins.TcpSocket) || null)) : null"),
    ("window.Capacitor&&Capacitor.registerPlugin?Capacitor.registerPlugin('ForegroundService'):null",
     "window.Capacitor?(Capacitor.registerPlugin?Capacitor.registerPlugin('ForegroundService'):((Capacitor.Plugins&&Capacitor.Plugins.ForegroundService)||null)):null"),
]
for old, new in pairs:
    if old not in s:
        raise SystemExit('::error::Hindi mahanap ang line na papalitan: ' + old[:60])
    s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('index.html patched OK (TcpSocket + ForegroundService)')
