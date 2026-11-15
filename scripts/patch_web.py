# Capacitor (walang bundler): walang Capacitor.registerPlugin, kaya gamitin ang Capacitor.Plugins.<Name>
p = 'www/index.html'
s = open(p, encoding='utf-8').read()

pairs = [
    ("window.Capacitor && Capacitor.registerPlugin ? Capacitor.registerPlugin('TcpSocket') : null",
     "window.Capacitor ? (Capacitor.registerPlugin ? Capacitor.registerPlugin('TcpSocket') : ((Capacitor.Plugins && Capacitor.Plugins.TcpSocket) || null)) : null"),
    ("window.Capacitor&&Capacitor.registerPlugin?Capacitor.registerPlugin('ForegroundService'):null",
     "window.Capacitor?(Capacitor.registerPlugin?Capacitor.registerPlugin('ForegroundService'):((Capacitor.Plugins&&Capacitor.Plugins.ForegroundService)||null)):null"),
    ("const b64 = (u) => { let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); };",
     "const b64 = (u) => { let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, new Uint8Array(u.buffer, u.byteOffset + i, Math.min(0x8000, u.length - i))); return btoa(s); };"),

    # --- Voice FX: pitch/ring branch ay naka-connect lang kapag ginagamit (bawas CPU kapag OFF) ---
    ("micGain.connect(dA);micGain.connect(dB);",
     "const pIn=G(1);pIn.connect(dA);pIn.connect(dB);"),
    ("micGain.connect(ringG);ringG.connect(ringOut);",
     "const rIn=G(1);rIn.connect(ringG);ringG.connect(ringOut);"),
    ("V.set=(m)=>{V.mode=m;const t=nowT();",
     "const on={p:0,r:0},want={p:0,r:0};const link=(k,node,w)=>{want[k]=w?1:0;if(w&&!on[k]){micGain.connect(node);on[k]=1}else if(!w&&on[k]){setTimeout(()=>{if(!want[k]&&on[k]){try{micGain.disconnect(node)}catch{}on[k]=0}},250)}};\n  V.set=(m)=>{V.mode=m;const t=nowT();"),
    ("const c=P[m]||P.off,pit=c.p!=null;",
     "const c=P[m]||P.off,pit=c.p!=null;link('p',pIn,pit);link('r',rIn,!!c.ring);"),
    # --- Voice FX: ang monitor (phone speaker/headphone), echo at reverb ay galing na sa boses na may FX ---
    ("vOut.connect(vRevS);vRevS.connect(vRev);vRev.connect(vRevO);vRevO.connect(master);",
     "vOut.connect(vRevS);vRevS.connect(vRev);vRev.connect(vRevO);vRevO.connect(master);\n  try{micGain.disconnect(echoDelay)}catch{}try{micGain.disconnect(mmHP)}catch{}try{micGain.disconnect(revSend)}catch{}\n  vOut.connect(echoDelay);vOut.connect(mmHP);vOut.connect(revSend);"),
    # --- Music: kapag binuksan ang mic, siguraduhing tuloy ang AudioContext at ang mga deck na tumutugtog ---
    ("  micSrc.connect(micIn);\n  btn.textContent = ",
     "  micSrc.connect(micIn);\n  try{const was=decks.map((d)=>!d.audio.paused);const kick=()=>{ctx.resume().catch(()=>{});decks.forEach((d,i)=>{if(was[i]&&d.audio.paused)d.audio.play().catch(()=>{})})};[250,800].forEach((t)=>setTimeout(kick,t))}catch{}\n  btn.textContent = "),
    # --- Credit sa ilalim ng Settings (Output Settings at Audio Settings) ---
    ("Done</button>\n</div>\n</div>\n\n<div class=\"modal\" id=\"eqModal\" hidden>",
     "Done</button>\n  <div style=\"text-align:center;margin-top:16px;font-size:12px;line-height:1.6;opacity:.85\">@The Groove Mixer<br>Created by DJBERMAS</div>\n</div>\n</div>\n\n<div class=\"modal\" id=\"eqModal\" hidden>"),
    ("Done</button>\n</div>\n</div>\n\n<div class=\"decks\">",
     "Done</button>\n  <div style=\"text-align:center;margin-top:16px;font-size:12px;line-height:1.6;opacity:.85\">@The Groove Mixer<br>Created by DJBERMAS</div>\n</div>\n</div>\n\n<div class=\"decks\">"),
]
for old, new in pairs:
    if s.count(old) != 1:
        raise SystemExit('::error::Hindi mahanap (o higit sa isa) ang line na papalitan: ' + old[:60])
    s = s.replace(old, new)


# ===== Tema na kasunod ng kulay ng logo (cyan / blue / purple / magenta sa itim) + bilog na logo =====
import base64
logo_b64 = base64.b64encode(open('logo_src.png', 'rb').read()).decode()

THEME = """
:root{--bg:#02030a;--panel:#0a0c18;--panel2:#12152c;--line:#1b2150;--txt:#eef4ff;--dim:#9db4e0;--c1:#00c6fe;--c2:#f4f8ff;--acc:#8314fc;--ok:#19e6a0;--live:#ff3b3b;--edge:#02030a}
html{background:#02030a}
body{background:radial-gradient(120% 38% at 50% -5%,#10205a 0,transparent 70%),radial-gradient(90% 30% at 100% 100%,#3a0a5e66 0,transparent 70%),linear-gradient(180deg,#050714,#02030a)}
h1{background:linear-gradient(90deg,#00c6fe,#055bfc 45%,#8314fc 72%,#f604f5);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 0 8px #055bfc88)}
label,.vl{color:#8fa6d6}
.card,.card#micCard{background:linear-gradient(180deg,#141a3a,#090c1c);border:1px solid #1b2a66;box-shadow:inset 0 1px 0 #6fb7ff1f,0 6px 16px #000c}
.card#micCard{box-shadow:inset 0 1px 0 #6fb7ff1f,0 -8px 24px #000d}
button:not(.pad){background:linear-gradient(180deg,#232b5c,#11163a);color:#dbe8ff;border:1px solid #0a0f2a;box-shadow:inset 0 1px 0 #7fb0ff26,0 1px 2px #000b}
button:not(.pad):active{background:linear-gradient(180deg,#0d1130,#1b2350)}
button.on:not(.pad){background:linear-gradient(180deg,#5be0ff,#00c6fe 40%,#055bfc);color:#02101e;text-shadow:none;border-color:#02245e;box-shadow:inset 0 1px 0 #ffffff77,0 0 14px #00c6fe99}
.deck button.on:not(.pad){background:linear-gradient(180deg,#ffffff55,#ffffff00 55%),var(--c);color:#04101c;box-shadow:inset 0 1px 0 #fff8,0 0 12px var(--c)}
#gearBtn,#mixBtn,#closeSettings,#closeMix,#closeEq,#fsBtn{background:radial-gradient(circle at 35% 28%,#2a3a8a,#141b48 60%,#070a1f);color:#bfe6ff;border:2px solid #02030a;box-shadow:inset 0 1px 0 #7fb0ff44,0 0 0 1px #00c6fe88,0 0 10px #055bfc66,0 3px 6px #000a}
#status{color:#7fd8ff}
#liveBtn:not(.live){filter:brightness(.85)}
.now,#status{background:linear-gradient(180deg,#03040c,#080b1e)}
input[type=range]{background:linear-gradient(90deg,var(--cc) var(--v),#03040c var(--v))}
input[type=text],input[type=password],input[type=number],select{background:linear-gradient(180deg,#03040c,#0a0e24);color:#eef4ff}
li{background:#0a0e24;color:#dbe8ff}
li.cur{background:#0f2a66;color:#fff}
#toast{border-color:#00c6fe;color:#bff1ff;background:#070a1c}
.spec{background:#02030a}
#rotHint{border-color:#00c6fe55;background:#07102a;color:#bff1ff}
#mixDl{border-color:#00c6fe;background:#070a1c}
#mixDl a{background:linear-gradient(180deg,#5be0ff,#00c6fe 45%,#055bfc);color:#02101e}
.gmLogo{width:64px;height:64px;border-radius:50%;background:#000 url(data:image/png;base64,__LOGO__) center/cover no-repeat;box-shadow:0 0 0 2px #00c6fe88,0 0 18px #055bfc99,0 0 30px #f604f544;flex:none}
.gmLogo.sm{width:46px;height:46px}
#gmFooter{display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px 0 26px;text-align:center;font-size:12px;line-height:1.6;color:#9db4e0}
.gmCred{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;margin-top:16px;font-size:12px;line-height:1.6;color:#9db4e0}
"""
s = s.replace('</head>', '<style id="gm-theme">' + THEME.replace('__LOGO__', logo_b64) + '</style>\n</head>', 1)
s = s.replace('<meta name="theme-color" content="#0b0c0f">', '<meta name="theme-color" content="#02030a">', 1)

# credit block sa loob ng settings: may bilog na logo sa itaas
OLD_CRED = '<div style="text-align:center;margin-top:16px;font-size:12px;line-height:1.6;opacity:.85">@The Groove Mixer<br>Created by DJBERMAS</div>'
NEW_CRED = '<div class="gmCred"><div class="gmLogo sm"></div>@The Groove Mixer<br>Created by DJBERMAS</div>'
if s.count(OLD_CRED) != 2:
    raise SystemExit('::error::Credit block: inaasahang 2, nakita ' + str(s.count(OLD_CRED)))
s = s.replace(OLD_CRED, NEW_CRED)

# footer sa dulo ng page: bilog na logo + credit
FOOTER = '<div id="gmFooter"><div class="gmLogo"></div><div>@The Groove Mixer<br>Created by DJBERMAS</div></div>\n\n'
i = s.index('\n<script>\n', s.index('<body>')) + 1
s = s[:i] + FOOTER + s[i:]

# ===== GO LIVE -> OFF AIR / ON AIR (pula) =====
RED = '\U0001F534'
for old, new, n in [
    (RED + '\nGO LIVE</button>', RED + '\nOFF AIR</button>', 1),
    ("'" + RED + "\\nGO LIVE'", "'" + RED + "\\nOFF AIR'", 2),
    ("'\u25A0\\nCANCEL'", "'" + RED + "\\nON AIR'", 1),
]:
    if s.count(old) != n:
        raise SystemExit('::error::Label ' + repr(old) + ' inaasahang ' + str(n) + ', nakita ' + str(s.count(old)))
    s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('index.html patched OK')
