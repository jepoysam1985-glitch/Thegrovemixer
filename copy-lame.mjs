// Kinokopya ang lame.min.js (MP3 encoder) mula sa node_modules papuntang www/
import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
const src = 'node_modules/lamejs/lame.min.js';
if (!existsSync(src)) { console.error('Wala ang lamejs. Patakbuhin muna: npm install'); process.exit(1); }
mkdirSync('www', { recursive: true });
copyFileSync(src, 'www/lame.min.js');
console.log('lame.min.js -> www/');
