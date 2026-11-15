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
    # --- Audio engine selector (Settings): para masubukan kung aling setup ang hindi pumuputol kapag ON ang mic ---
    ("const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 44100, latencyHint: 'balanced' });",
     "const __ae = (() => { try { return localStorage.getItem('jfm_ae') || 'a'; } catch (e) { return 'a'; } })();\nconst ctx = new (window.AudioContext || window.webkitAudioContext)(__ae === 'b' ? { latencyHint: 'balanced' } : __ae === 'd' ? { sampleRate: 44100, latencyHint: 'playback' } : { sampleRate: 44100, latencyHint: 'balanced' });"),
    ("  <button id=\"closeSettings2\" style=\"width:100%;height:50px;margin-top:14px;",
     "  <label for=\"aeSel\">Audio engine (close and reopen the app after changing)</label>\n  <select id=\"aeSel\" onchange=\"try{localStorage.setItem('jfm_ae',this.value)}catch(e){}try{toast('Saved. Close and reopen the app to apply.')}catch(e){}\">\n    <option value=\"a\">Default (44.1 kHz)</option>\n    <option value=\"b\">Phone native rate (try if music chops with mic)</option>\n    <option value=\"d\">Bigger buffer (more stable, slight delay)</option>\n  </select>\n  <script>try{document.getElementById('aeSel').value=localStorage.getItem('jfm_ae')||'a'}catch(e){}</script>\n  <button id=\"closeSettings2\" style=\"width:100%;height:50px;margin-top:14px;"),
]
for old, new in pairs:
    if s.count(old) != 1:
        raise SystemExit('::error::Hindi mahanap (o higit sa isa) ang line na papalitan: ' + old[:60])
    s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('index.html patched OK')
