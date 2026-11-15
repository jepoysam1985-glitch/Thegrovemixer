# THE GROOVE MIXER (Capacitor)

## Para sa GitHub (auto-build ng APK)
1. Gumawa ng bagong repo, i-push ang lahat ng laman ng folder na ito.
2. Pumunta sa **Actions** → **Build Android APK** (kusang tatakbo sa bawat push).
3. Pagkatapos, i-download ang `groove-mixer-debug-apk` sa **Artifacts** at i-install sa phone.

## Local build
```bash
npm install
npm run android:add   # isang beses lang
npm run sync
npm run android:open  # buksan sa Android Studio
```

## Notes
- `www/index.html` ang app. I-edit lang ito, tapos `npm run sync`.
- `lame.min.js` ay awtomatikong kinokopya mula sa `lamejs` package.
- Naka-save ang mga recording sa `Documents/GrooveMixer/`.
- Palitan ang `appId` sa `capacitor.config.json` kung gusto mo ng sarili mong package name.
