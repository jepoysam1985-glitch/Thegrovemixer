# Compat para sa Android 9 hanggang pinakamataas: polyfill sa lumang WebView at ayos sa syntax.
# Ligtas patakbuhin ulit (hindi nagdodoble).
import re

p = 'www/index.html'
s = open(p, encoding='utf-8').read()
if 'id="gm-compat"' in s:
    print('compat: naka-patch na')
    raise SystemExit(0)

# 1) optional catch binding (catch {}) -> catch (_e) {}  (para gumana kahit sa WebView na mas luma sa Chrome 66)
s, n = re.subn(r'\bcatch\s*\{', 'catch(_e){', s)
print('compat: catch {} naayos =', n)

# 2) polyfill + paalala kapag luma ang WebView
POLY = r'''<script id="gm-compat">
/* Compat para sa lumang Android WebView (Android 9 at pataas) */
(function(){
  try{
    if(typeof Blob!=='undefined'&&!Blob.prototype.arrayBuffer){Blob.prototype.arrayBuffer=function(){var b=this;return new Promise(function(res,rej){var r=new FileReader();r.onload=function(){res(r.result)};r.onerror=function(){rej(r.error)};r.readAsArrayBuffer(b)})}}
    if(typeof Blob!=='undefined'&&!Blob.prototype.text){Blob.prototype.text=function(){var b=this;return new Promise(function(res,rej){var r=new FileReader();r.onload=function(){res(r.result)};r.onerror=function(){rej(r.error)};r.readAsText(b)})}}
    if(typeof Element!=='undefined'&&!Element.prototype.replaceChildren){Element.prototype.replaceChildren=function(){while(this.firstChild)this.removeChild(this.firstChild);for(var i=0;i<arguments.length;i++){var n=arguments[i];this.appendChild(typeof n==='string'?document.createTextNode(n):n)}}}
    if(!Array.prototype.flatMap){Object.defineProperty(Array.prototype,'flatMap',{configurable:true,writable:true,value:function(f,t){var o=[];for(var i=0;i<this.length;i++){var v=f.call(t,this[i],i,this);if(Array.isArray(v)){for(var j=0;j<v.length;j++)o.push(v[j])}else o.push(v)}return o}})}
    if(!Array.prototype.flat){Object.defineProperty(Array.prototype,'flat',{configurable:true,writable:true,value:function(d){d=d===undefined?1:d;var o=[];(function w(a,l){for(var i=0;i<a.length;i++){if(Array.isArray(a[i])&&l>0)w(a[i],l-1);else o.push(a[i])}})(this,d);return o}})}
    if(!Array.prototype.at){Object.defineProperty(Array.prototype,'at',{configurable:true,writable:true,value:function(i){i=Math.trunc(i)||0;if(i<0)i+=this.length;return this[i]}})}
    if(!String.prototype.at){Object.defineProperty(String.prototype,'at',{configurable:true,writable:true,value:function(i){i=Math.trunc(i)||0;if(i<0)i+=this.length;return this.charAt(i)}})}
    if(!String.prototype.replaceAll){String.prototype.replaceAll=function(a,b){if(a instanceof RegExp)return this.replace(a,b);var e=String(a).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');return this.replace(new RegExp(e,'g'),b)}}
    if(!Object.fromEntries){Object.fromEntries=function(it){var o={};for(var e of it)o[e[0]]=e[1];return o}}
    if(!Promise.allSettled){Promise.allSettled=function(a){return Promise.all(Array.prototype.map.call(a,function(p){return Promise.resolve(p).then(function(v){return{status:'fulfilled',value:v}},function(r){return{status:'rejected',reason:r}})}))}}
  }catch(e){}
  try{
    var m=/Chrome\/(\d+)/.exec(navigator.userAgent);
    if(m&&+m[1]<84){window.addEventListener('load',function(){setTimeout(function(){try{toast('Luma ang Android System WebView (v'+m[1]+'). I-update ito sa Play Store para gumana nang tama ang lahat.')}catch(e){}},3500)})}
  }catch(e){}
})();
</script>
'''
i = s.index('<head>') + len('<head>')
s = s[:i] + '\n' + POLY + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('compat: polyfill idinagdag')
