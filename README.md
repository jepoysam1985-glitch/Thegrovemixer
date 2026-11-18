# 🎧 THE GROOVE MIXER

**DJ + Radio Broadcasting app para sa Android.**
Gawing sariling DJ console at radio station ang phone mo: dalawang deck, 50-slot effects board, mic na may voice effects, at **GO LIVE** diretso sa server.

## ⬇️ Download (APK)
Kunin ang pinakabagong `THE-GROOVE-MIXER.apk` sa **[Releases](../../releases)**.
Kung first time mag-install ng APK, i-allow muna ang **"Install unknown apps"** sa Settings ng phone. Android 9 pataas.

---

## 🎚 DJ Decks
- Dalawang deck (Deck 1 at Deck 2) na may jog wheel
- Crossfader at volume fader ng bawat deck
- Pitch/tempo slider at **TAP BPM**
- **SYNC** at **BEAT-MATCH**
- **AUTO-MIX** at **FADE OUT**
- **Auto fade** papunta sa Deck 1 o Deck 2 (cut, 4, 8, 16 o 32 beats)
- **Scratch**, **Slip**, **Reverse**
- **Key detect** at manual **beatgrid**
- **4 Hot Cue pads** bawat deck
- **Loops** na 1, 2, 4 at 8 beats
- Waveform at spectrum bawat deck
- Music level meter, MUTE at LOCK
- I-save at i-load ang playlist (**LISTS**)

## 🔔 Effects Board (50 slots)
- 50 pad ng sarili mong sound effects: airhorn, jingle, station ID, o kahit anong audio file
- **Edit slots** para palitan ang laman ng bawat pad
- **Stop all** para patayin lahat ng tumutugtog na effect
- **Auto-jingle**: kusang tumutunog ang effect kada 3 o 5 kanta, o kada 10 o 15 minuto
- Puwedeng piliin kung aling effect ang gagamitin, o random

## 🎛 DJ FX
- Echo, Reverb, Flanger, Phaser
- Bit-crush, Gate, Karaoke
- Roll at Stutter (1/2, 1/4, 1/8, 1/16)
- Filter (LPF/HPF) bawat deck
- Siren, Riser at Fall sound effects

## 🎤 Mic
- **Push-to-talk** (bukas lang ang mic habang hawak ang button)
- **Voice effects:** Male, Female, Child, Chipmunk, High, Deep, Monster, Demon, Robot, Alien, Phone, Megaphone, Radio, Hall, Cave
- Noise reduction
- **Auto-duck**: kusang humihina ang musika kapag nagsasalita
- Sariling Mic EQ

## 🔊 EQ
- Master EQ na may presets: Flat, Pop, Rock, Jazz, Club, Dance, Hip-Hop, Techno, Acoustic, Vocal, Bass Boost, Treble Boost

## 📡 GO LIVE (Radio Streaming)
- Diretso sa **Icecast** at **Shoutcast (v1)**
- MP3 encoding; puwedeng palitan ang bitrate habang live (48 hanggang 192 kbps)
- Kusang bumababa ang bitrate kapag mahina ang connection
- Auto-reconnect kapag naputol
- Kusang pinapadala ang now-playing title sa server at sa website
- **Monitor/CUE**: maririnig mo ang halo mo sa headphone o Bluetooth, hindi kasama sa stream

## ⏺ REC
- Mag-record ng mix. Naka-save sa `Documents/GrooveMixer`

## 📱 App
- Landscape at fullscreen na wide screen
- Tuloy ang tugtog kahit nasa background

---

## Build
Awtomatikong nagbi-build ng APK ang GitHub Actions (**Build APK**) sa bawat push sa `main`.
Ang APK ay nasa **Releases** (`THE-GROOVE-MIXER.apk`) at nasa Actions run bilang artifact na `THE-GROOVE-MIXER-apk`.

### Local build
```bash
npm install
npm run android:add   # isang beses lang
npm run sync
npm run android:open  # buksan sa Android Studio
```

### Notes
- `index.html` ang mismong app; ang workflow ang naglalagay nito sa `www/` bago mag-sync.
- `lame.min.js` (MP3 encoder) ay awtomatikong kinokopya mula sa `lamejs` package.
- Palitan ang `appId` sa `capacitor.config.json` kung gusto mo ng sarili mong package name.
