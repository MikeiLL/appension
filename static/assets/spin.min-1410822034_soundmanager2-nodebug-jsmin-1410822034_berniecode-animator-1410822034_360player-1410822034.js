//fgnass.github.com/spin.js#v1.2.7
!function(e,t,n){function o(e,n){var r=t.createElement(e||"div"),i;for(i in n)r[i]=n[i];return r}function u(e){for(var t=1,n=arguments.length;t<n;t++)e.appendChild(arguments[t]);return e}function f(e,t,n,r){var o=["opacity",t,~~(e*100),n,r].join("-"),u=.01+n/r*100,f=Math.max(1-(1-e)/t*(100-u),e),l=s.substring(0,s.indexOf("Animation")).toLowerCase(),c=l&&"-"+l+"-"||"";return i[o]||(a.insertRule("@"+c+"keyframes "+o+"{"+"0%{opacity:"+f+"}"+u+"%{opacity:"+e+"}"+(u+.01)+"%{opacity:1}"+(u+t)%100+"%{opacity:"+e+"}"+"100%{opacity:"+f+"}"+"}",a.cssRules.length),i[o]=1),o}function l(e,t){var i=e.style,s,o;if(i[t]!==n)return t;t=t.charAt(0).toUpperCase()+t.slice(1);for(o=0;o<r.length;o++){s=r[o]+t;if(i[s]!==n)return s}}function c(e,t){for(var n in t)e.style[l(e,n)||n]=t[n];return e}function h(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var i in r)e[i]===n&&(e[i]=r[i])}return e}function p(e){var t={x:e.offsetLeft,y:e.offsetTop};while(e=e.offsetParent)t.x+=e.offsetLeft,t.y+=e.offsetTop;return t}var r=["webkit","Moz","ms","O"],i={},s,a=function(){var e=o("style",{type:"text/css"});return u(t.getElementsByTagName("head")[0],e),e.sheet||e.styleSheet}(),d={lines:12,length:7,width:5,radius:10,rotate:0,corners:1,color:"#000",speed:1,trail:100,opacity:.25,fps:20,zIndex:2e9,className:"spinner",top:"auto",left:"auto",position:"relative"},v=function m(e){if(!this.spin)return new m(e);this.opts=h(e||{},m.defaults,d)};v.defaults={},h(v.prototype,{spin:function(e){this.stop();var t=this,n=t.opts,r=t.el=c(o(0,{className:n.className}),{position:n.position,width:0,zIndex:n.zIndex}),i=n.radius+n.length+n.width,u,a;e&&(e.insertBefore(r,e.firstChild||null),a=p(e),u=p(r),c(r,{left:(n.left=="auto"?a.x-u.x+(e.offsetWidth>>1):parseInt(n.left,10)+i)+"px",top:(n.top=="auto"?a.y-u.y+(e.offsetHeight>>1):parseInt(n.top,10)+i)+"px"})),r.setAttribute("aria-role","progressbar"),t.lines(r,t.opts);if(!s){var f=0,l=n.fps,h=l/n.speed,d=(1-n.opacity)/(h*n.trail/100),v=h/n.lines;(function m(){f++;for(var e=n.lines;e;e--){var i=Math.max(1-(f+e*v)%h*d,n.opacity);t.opacity(r,n.lines-e,i,n)}t.timeout=t.el&&setTimeout(m,~~(1e3/l))})()}return t},stop:function(){var e=this.el;return e&&(clearTimeout(this.timeout),e.parentNode&&e.parentNode.removeChild(e),this.el=n),this},lines:function(e,t){function i(e,r){return c(o(),{position:"absolute",width:t.length+t.width+"px",height:t.width+"px",background:e,boxShadow:r,transformOrigin:"left",transform:"rotate("+~~(360/t.lines*n+t.rotate)+"deg) translate("+t.radius+"px"+",0)",borderRadius:(t.corners*t.width>>1)+"px"})}var n=0,r;for(;n<t.lines;n++)r=c(o(),{position:"absolute",top:1+~(t.width/2)+"px",transform:t.hwaccel?"translate3d(0,0,0)":"",opacity:t.opacity,animation:s&&f(t.opacity,t.trail,n,t.lines)+" "+1/t.speed+"s linear infinite"}),t.shadow&&u(r,c(i("#000","0 0 4px #000"),{top:"2px"})),u(e,u(r,i(t.color,"0 0 1px rgba(0,0,0,.1)")));return e},opacity:function(e,t,n){t<e.childNodes.length&&(e.childNodes[t].style.opacity=n)}}),function(){function e(e,t){return o("<"+e+' xmlns="urn:schemas-microsoft.com:vml" class="spin-vml">',t)}var t=c(o("group"),{behavior:"url(#default#VML)"});!l(t,"transform")&&t.adj?(a.addRule(".spin-vml","behavior:url(#default#VML)"),v.prototype.lines=function(t,n){function s(){return c(e("group",{coordsize:i+" "+i,coordorigin:-r+" "+ -r}),{width:i,height:i})}function l(t,i,o){u(a,u(c(s(),{rotation:360/n.lines*t+"deg",left:~~i}),u(c(e("roundrect",{arcsize:n.corners}),{width:r,height:n.width,left:n.radius,top:-n.width>>1,filter:o}),e("fill",{color:n.color,opacity:n.opacity}),e("stroke",{opacity:0}))))}var r=n.length+n.width,i=2*r,o=-(n.width+n.length)*2+"px",a=c(s(),{position:"absolute",top:o,left:o}),f;if(n.shadow)for(f=1;f<=n.lines;f++)l(f,-2,"progid:DXImageTransform.Microsoft.Blur(pixelradius=2,makeshadow=1,shadowopacity=.3)");for(f=1;f<=n.lines;f++)l(f);return u(t,a)},v.prototype.opacity=function(e,t,n,r){var i=e.firstChild;r=r.shadow&&r.lines||0,i&&t+r<i.childNodes.length&&(i=i.childNodes[t+r],i=i&&i.firstChild,i=i&&i.firstChild,i&&(i.opacity=n))}):s=l(t,"animation")}(),typeof define=="function"&&define.amd?define(function(){return v}):e.Spinner=v}(window,document);

window.__spinner = new Spinner({
  lines: 9, // The number of lines to draw
  length: 0, // The length of each line
  width: 7, // The line thickness
  radius: 38, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  color: '#000', // #rgb or #rrggbb
  speed: 0.9, // Rounds per second
  trail: 25, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: true, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: 'auto', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
});

/** @license
 *
 * SoundManager 2: JavaScript Sound for the Web
 * ----------------------------------------------
 * http://schillmania.com/projects/soundmanager2/
 *
 * Copyright (c) 2007, Scott Schiller. All rights reserved.
 * Code provided under the BSD License:
 * http://schillmania.com/projects/soundmanager2/license.txt
 *
 * V2.97a.20120916
 */
(function(fa){function R(R,ea){function S(a){return c.preferFlash&&y&&!c.ignoreFlash&&"undefined"!==typeof c.flash[a]&&c.flash[a]}function l(a){return function(c){var d=this._t;return!d||!d._a?null:a.call(this,c)}}this.setupOptions={url:R||null,flashVersion:8,debugMode:!0,debugFlash:!1,useConsole:!0,consoleOnly:!0,waitForWindowLoad:!1,bgColor:"#ffffff",useHighPerformance:!1,flashPollingInterval:null,html5PollingInterval:null,flashLoadTimeout:1E3,wmode:null,allowScriptAccess:"always",useFlashBlock:!1,
useHTML5Audio:!0,html5Test:/^(probably|maybe)$/i,preferFlash:!0,noSWFCache:!1};this.defaultOptions={autoLoad:!1,autoPlay:!1,from:null,loops:1,onid3:null,onload:null,whileloading:null,onplay:null,onpause:null,onresume:null,whileplaying:null,onposition:null,onstop:null,onfailure:null,onfinish:null,multiShot:!0,multiShotEvents:!1,position:null,pan:0,stream:!0,to:null,type:null,usePolicyFile:!1,volume:100};this.flash9Options={isMovieStar:null,usePeakData:!1,useWaveformData:!1,useEQData:!1,onbufferchange:null,
ondataerror:null};this.movieStarOptions={bufferTime:3,serverURL:null,onconnect:null,duration:null};this.audioFormats={mp3:{type:['audio/mpeg; codecs="mp3"',"audio/mpeg","audio/mp3","audio/MPA","audio/mpa-robust"],required:!0},mp4:{related:["aac","m4a","m4b"],type:['audio/mp4; codecs="mp4a.40.2"',"audio/aac","audio/x-m4a","audio/MP4A-LATM","audio/mpeg4-generic"],required:!1},ogg:{type:["audio/ogg; codecs=vorbis"],required:!1},wav:{type:['audio/wav; codecs="1"',"audio/wav","audio/wave","audio/x-wav"],
required:!1}};this.movieID="sm2-container";this.id=ea||"sm2movie";this.debugID="soundmanager-debug";this.debugURLParam=/([#?&])debug=1/i;this.versionNumber="V2.97a.20120916";this.altURL=this.movieURL=this.version=null;this.enabled=this.swfLoaded=!1;this.oMC=null;this.sounds={};this.soundIDs=[];this.didFlashBlock=this.muted=!1;this.filePattern=null;this.filePatterns={flash8:/\.mp3(\?.*)?$/i,flash9:/\.mp3(\?.*)?$/i};this.features={buffering:!1,peakData:!1,waveformData:!1,eqData:!1,movieStar:!1};this.sandbox=
{};var ga;try{ga="undefined"!==typeof Audio&&"undefined"!==typeof(ha&&10>opera.version()?new Audio(null):new Audio).canPlayType}catch(Za){ga=!1}this.hasHTML5=ga;this.html5={usingFlash:null};this.flash={};this.ignoreFlash=this.html5Only=!1;var Da,c=this,i=null,T,q=navigator.userAgent,h=fa,ia=h.location.href.toString(),m=document,ja,Ea,ka,j,v=[],J=!1,K=!1,k=!1,s=!1,la=!1,L,r,ma,U,na,B,C,D,Fa,oa,V,W,E,pa,M,qa,X,F,Ga,ra,Ha,Y,Ia,N=null,sa=null,t,ta,G,Z,$,H,p,O=!1,ua=!1,Ja,Ka,La,aa=0,P=null,ba,n=null,Ma,
ca,Q,w,va,wa,Na,o,Wa=Array.prototype.slice,z=!1,y,xa,Oa,u,Pa,ya=q.match(/(ipad|iphone|ipod)/i),x=q.match(/msie/i),Xa=q.match(/webkit/i),za=q.match(/safari/i)&&!q.match(/chrome/i),ha=q.match(/opera/i),Aa=q.match(/(mobile|pre\/|xoom)/i)||ya,Qa=!ia.match(/usehtml5audio/i)&&!ia.match(/sm2\-ignorebadua/i)&&za&&!q.match(/silk/i)&&q.match(/OS X 10_6_([3-7])/i),Ba="undefined"!==typeof m.hasFocus?m.hasFocus():null,da=za&&("undefined"===typeof m.hasFocus||!m.hasFocus()),Ra=!da,Sa=/(mp3|mp4|mpa|m4a|m4b)/i,Ca=
m.location?m.location.protocol.match(/http/i):null,Ta=!Ca?"http://":"",Ua=/^\s*audio\/(?:x-)?(?:mpeg4|aac|flv|mov|mp4||m4v|m4a|m4b|mp4v|3gp|3g2)\s*(?:$|;)/i,Va="mpeg4,aac,flv,mov,mp4,m4v,f4v,m4a,m4b,mp4v,3gp,3g2".split(","),Ya=RegExp("\\.("+Va.join("|")+")(\\?.*)?$","i");this.mimePattern=/^\s*audio\/(?:x-)?(?:mp(?:eg|3))\s*(?:$|;)/i;this.useAltURL=!Ca;this._global_a=null;if(Aa&&(c.useHTML5Audio=!0,c.preferFlash=!1,ya))z=c.ignoreFlash=!0;this.setup=function(a){var e=!c.url;"undefined"!==typeof a&&
k&&n&&c.ok()&&("undefined"!==typeof a.flashVersion||"undefined"!==typeof a.url)&&H(t("setupLate"));ma(a);e&&M&&"undefined"!==typeof a.url&&c.beginDelayedInit();!M&&"undefined"!==typeof a.url&&"complete"===m.readyState&&setTimeout(E,1);return c};this.supported=this.ok=function(){return n?k&&!s:c.useHTML5Audio&&c.hasHTML5};this.getMovie=function(a){return T(a)||m[a]||h[a]};this.createSound=function(a,e){function d(){b=Z(b);c.sounds[f.id]=new Da(f);c.soundIDs.push(f.id);return c.sounds[f.id]}var b=null,
g=null,f=null;if(!k||!c.ok())return H(void 0),!1;"undefined"!==typeof e&&(a={id:a,url:e});b=r(a);b.url=ba(b.url);f=b;if(p(f.id,!0))return c.sounds[f.id];if(ca(f))g=d(),g._setup_html5(f);else{if(8<j&&null===f.isMovieStar)f.isMovieStar=!(!f.serverURL&&!(f.type&&f.type.match(Ua)||f.url.match(Ya)));f=$(f,void 0);g=d();if(8===j)i._createSound(f.id,f.loops||1,f.usePolicyFile);else if(i._createSound(f.id,f.url,f.usePeakData,f.useWaveformData,f.useEQData,f.isMovieStar,f.isMovieStar?f.bufferTime:!1,f.loops||
1,f.serverURL,f.duration||null,f.autoPlay,!0,f.autoLoad,f.usePolicyFile),!f.serverURL)g.connected=!0,f.onconnect&&f.onconnect.apply(g);!f.serverURL&&(f.autoLoad||f.autoPlay)&&g.load(f)}!f.serverURL&&f.autoPlay&&g.play();return g};this.destroySound=function(a,e){if(!p(a))return!1;var d=c.sounds[a],b;d._iO={};d.stop();d.unload();for(b=0;b<c.soundIDs.length;b++)if(c.soundIDs[b]===a){c.soundIDs.splice(b,1);break}e||d.destruct(!0);delete c.sounds[a];return!0};this.load=function(a,e){return!p(a)?!1:c.sounds[a].load(e)};
this.unload=function(a){return!p(a)?!1:c.sounds[a].unload()};this.onposition=this.onPosition=function(a,e,d,b){return!p(a)?!1:c.sounds[a].onposition(e,d,b)};this.clearOnPosition=function(a,e,d){return!p(a)?!1:c.sounds[a].clearOnPosition(e,d)};this.start=this.play=function(a,e){var d=!1;if(!k||!c.ok())return H("soundManager.play(): "+t(!k?"notReady":"notOK")),d;if(!p(a)){e instanceof Object||(e={url:e});if(e&&e.url)e.id=a,d=c.createSound(e).play();return d}return c.sounds[a].play(e)};this.setPosition=
function(a,e){return!p(a)?!1:c.sounds[a].setPosition(e)};this.stop=function(a){return!p(a)?!1:c.sounds[a].stop()};this.stopAll=function(){for(var a in c.sounds)c.sounds.hasOwnProperty(a)&&c.sounds[a].stop()};this.pause=function(a){return!p(a)?!1:c.sounds[a].pause()};this.pauseAll=function(){var a;for(a=c.soundIDs.length-1;0<=a;a--)c.sounds[c.soundIDs[a]].pause()};this.resume=function(a){return!p(a)?!1:c.sounds[a].resume()};this.resumeAll=function(){var a;for(a=c.soundIDs.length-1;0<=a;a--)c.sounds[c.soundIDs[a]].resume()};
this.togglePause=function(a){return!p(a)?!1:c.sounds[a].togglePause()};this.setPan=function(a,e){return!p(a)?!1:c.sounds[a].setPan(e)};this.setVolume=function(a,e){return!p(a)?!1:c.sounds[a].setVolume(e)};this.mute=function(a){var e=0;"string"!==typeof a&&(a=null);if(a)return!p(a)?!1:c.sounds[a].mute();for(e=c.soundIDs.length-1;0<=e;e--)c.sounds[c.soundIDs[e]].mute();return c.muted=!0};this.muteAll=function(){c.mute()};this.unmute=function(a){"string"!==typeof a&&(a=null);if(a)return!p(a)?!1:c.sounds[a].unmute();
for(a=c.soundIDs.length-1;0<=a;a--)c.sounds[c.soundIDs[a]].unmute();c.muted=!1;return!0};this.unmuteAll=function(){c.unmute()};this.toggleMute=function(a){return!p(a)?!1:c.sounds[a].toggleMute()};this.getMemoryUse=function(){var a=0;i&&8!==j&&(a=parseInt(i._getMemoryUse(),10));return a};this.disable=function(a){var e;"undefined"===typeof a&&(a=!1);if(s)return!1;s=!0;for(e=c.soundIDs.length-1;0<=e;e--)Ha(c.sounds[c.soundIDs[e]]);L(a);o.remove(h,"load",C);return!0};this.canPlayMIME=function(a){var e;
c.hasHTML5&&(e=Q({type:a}));!e&&n&&(e=a&&c.ok()?!!(8<j&&a.match(Ua)||a.match(c.mimePattern)):null);return e};this.canPlayURL=function(a){var e;c.hasHTML5&&(e=Q({url:a}));!e&&n&&(e=a&&c.ok()?!!a.match(c.filePattern):null);return e};this.canPlayLink=function(a){return"undefined"!==typeof a.type&&a.type&&c.canPlayMIME(a.type)?!0:c.canPlayURL(a.href)};this.getSoundById=function(a){if(!a)throw Error("soundManager.getSoundById(): sID is null/undefined");return c.sounds[a]};this.onready=function(a,c){var d=
!1;if("function"===typeof a)c||(c=h),na("onready",a,c),B();else throw t("needFunction","onready");return!0};this.ontimeout=function(a,c){var d=!1;if("function"===typeof a)c||(c=h),na("ontimeout",a,c),B({type:"ontimeout"});else throw t("needFunction","ontimeout");return!0};this._wD=this._writeDebug=function(){return!0};this._debug=function(){};this.reboot=function(){var a,e;for(a=c.soundIDs.length-1;0<=a;a--)c.sounds[c.soundIDs[a]].destruct();if(i)try{if(x)sa=i.innerHTML;N=i.parentNode.removeChild(i)}catch(d){}sa=
N=n=null;c.enabled=M=k=O=ua=J=K=s=c.swfLoaded=!1;c.soundIDs=[];c.sounds={};i=null;for(a in v)if(v.hasOwnProperty(a))for(e=v[a].length-1;0<=e;e--)v[a][e].fired=!1;h.setTimeout(c.beginDelayedInit,20)};this.getMoviePercent=function(){return i&&"undefined"!==typeof i.PercentLoaded?i.PercentLoaded():null};this.beginDelayedInit=function(){la=!0;E();setTimeout(function(){if(ua)return!1;X();W();return ua=!0},20);D()};this.destruct=function(){c.disable(!0)};Da=function(a){var e,d,b=this,g,f,A,I,h,m,l=!1,k=
[],o=0,q,s,n=null;e=null;d=null;this.sID=this.id=a.id;this.url=a.url;this._iO=this.instanceOptions=this.options=r(a);this.pan=this.options.pan;this.volume=this.options.volume;this.isHTML5=!1;this._a=null;this.id3={};this._debug=function(){};this.load=function(a){var c=null;if("undefined"!==typeof a)b._iO=r(a,b.options),b.instanceOptions=b._iO;else if(a=b.options,b._iO=a,b.instanceOptions=b._iO,n&&n!==b.url)b._iO.url=b.url,b.url=null;if(!b._iO.url)b._iO.url=b.url;b._iO.url=ba(b._iO.url);if(b._iO.url===
b.url&&0!==b.readyState&&2!==b.readyState)return 3===b.readyState&&b._iO.onload&&b._iO.onload.apply(b,[!!b.duration]),b;a=b._iO;n=b.url&&b.url.toString?b.url.toString():null;b.loaded=!1;b.readyState=1;b.playState=0;b.id3={};if(ca(a)){if(c=b._setup_html5(a),!c._called_load){b._html5_canplay=!1;if(b._a.src!==a.url)b._a.src=a.url,b.setPosition(0);b._a.autobuffer="auto";b._a.preload="auto";c._called_load=!0;a.autoPlay&&b.play()}}else try{b.isHTML5=!1,b._iO=$(Z(a)),a=b._iO,8===j?i._load(b.id,a.url,a.stream,
a.autoPlay,a.whileloading?1:0,a.loops||1,a.usePolicyFile):i._load(b.id,a.url,!!a.stream,!!a.autoPlay,a.loops||1,!!a.autoLoad,a.usePolicyFile)}catch(e){F({type:"SMSOUND_LOAD_JS_EXCEPTION",fatal:!0})}b.url=a.url;return b};this.unload=function(){if(0!==b.readyState){if(b.isHTML5){if(I(),b._a)b._a.pause(),va(b._a,"about:blank"),b.url="about:blank"}else 8===j?i._unload(b.id,"about:blank"):i._unload(b.id);g()}return b};this.destruct=function(a){if(b.isHTML5){if(I(),b._a)b._a.pause(),va(b._a),z||A(),b._a._t=
null,b._a=null}else b._iO.onfailure=null,i._destroySound(b.id);a||c.destroySound(b.id,!0)};this.start=this.play=function(a,c){var e,d;d=!0;d=null;c="undefined"===typeof c?!0:c;a||(a={});if(b.url)b._iO.url=b.url;b._iO=r(b._iO,b.options);b._iO=r(a,b._iO);b._iO.url=ba(b._iO.url);b.instanceOptions=b._iO;if(b._iO.serverURL&&!b.connected)return b.getAutoPlay()||b.setAutoPlay(!0),b;ca(b._iO)&&(b._setup_html5(b._iO),h());if(1===b.playState&&!b.paused)(e=b._iO.multiShot)||(d=b);if(null!==d)return d;a.url&&
a.url!==b.url&&b.load(b._iO);if(!b.loaded)if(0===b.readyState){if(!b.isHTML5)b._iO.autoPlay=!0;b.load(b._iO)}else 2===b.readyState&&(d=b);if(null!==d)return d;if(!b.isHTML5&&9===j&&0<b.position&&b.position===b.duration)a.position=0;if(b.paused&&0<=b.position&&(!b._iO.serverURL||0<b.position))b.resume();else{b._iO=r(a,b._iO);if(null!==b._iO.from&&null!==b._iO.to&&0===b.instanceCount&&0===b.playState&&!b._iO.serverURL){e=function(){b._iO=r(a,b._iO);b.play(b._iO)};if(b.isHTML5&&!b._html5_canplay)b.load({_oncanplay:e}),
d=!1;else if(!b.isHTML5&&!b.loaded&&(!b.readyState||2!==b.readyState))b.load({onload:e}),d=!1;if(null!==d)return d;b._iO=s()}(!b.instanceCount||b._iO.multiShotEvents||!b.isHTML5&&8<j&&!b.getAutoPlay())&&b.instanceCount++;b._iO.onposition&&0===b.playState&&m(b);b.playState=1;b.paused=!1;b.position="undefined"!==typeof b._iO.position&&!isNaN(b._iO.position)?b._iO.position:0;if(!b.isHTML5)b._iO=$(Z(b._iO));b._iO.onplay&&c&&(b._iO.onplay.apply(b),l=!0);b.setVolume(b._iO.volume,!0);b.setPan(b._iO.pan,
!0);b.isHTML5?(h(),d=b._setup_html5(),b.setPosition(b._iO.position),d.play()):(d=i._start(b.id,b._iO.loops||1,9===j?b._iO.position:b._iO.position/1E3,b._iO.multiShot),9===j&&!d&&b._iO.onplayerror&&b._iO.onplayerror.apply(b))}return b};this.stop=function(a){var c=b._iO;if(1===b.playState){b._onbufferchange(0);b._resetOnPosition(0);b.paused=!1;if(!b.isHTML5)b.playState=0;q();c.to&&b.clearOnPosition(c.to);if(b.isHTML5){if(b._a)a=b.position,b.setPosition(0),b.position=a,b._a.pause(),b.playState=0,b._onTimer(),
I()}else i._stop(b.id,a),c.serverURL&&b.unload();b.instanceCount=0;b._iO={};c.onstop&&c.onstop.apply(b)}return b};this.setAutoPlay=function(a){b._iO.autoPlay=a;b.isHTML5||(i._setAutoPlay(b.id,a),a&&!b.instanceCount&&1===b.readyState&&b.instanceCount++)};this.getAutoPlay=function(){return b._iO.autoPlay};this.setPosition=function(a){"undefined"===typeof a&&(a=0);var c=b.isHTML5?Math.max(a,0):Math.min(b.duration||b._iO.duration,Math.max(a,0));b.position=c;a=b.position/1E3;b._resetOnPosition(b.position);
b._iO.position=c;if(b.isHTML5){if(b._a&&b._html5_canplay&&b._a.currentTime!==a)try{b._a.currentTime=a,(0===b.playState||b.paused)&&b._a.pause()}catch(e){}}else a=9===j?b.position:a,b.readyState&&2!==b.readyState&&i._setPosition(b.id,a,b.paused||!b.playState,b._iO.multiShot);b.isHTML5&&b.paused&&b._onTimer(!0);return b};this.pause=function(a){if(b.paused||0===b.playState&&1!==b.readyState)return b;b.paused=!0;b.isHTML5?(b._setup_html5().pause(),I()):(a||"undefined"===typeof a)&&i._pause(b.id,b._iO.multiShot);
b._iO.onpause&&b._iO.onpause.apply(b);return b};this.resume=function(){var a=b._iO;if(!b.paused)return b;b.paused=!1;b.playState=1;b.isHTML5?(b._setup_html5().play(),h()):(a.isMovieStar&&!a.serverURL&&b.setPosition(b.position),i._pause(b.id,a.multiShot));!l&&a.onplay?(a.onplay.apply(b),l=!0):a.onresume&&a.onresume.apply(b);return b};this.togglePause=function(){if(0===b.playState)return b.play({position:9===j&&!b.isHTML5?b.position:b.position/1E3}),b;b.paused?b.resume():b.pause();return b};this.setPan=
function(a,c){"undefined"===typeof a&&(a=0);"undefined"===typeof c&&(c=!1);b.isHTML5||i._setPan(b.id,a);b._iO.pan=a;if(!c)b.pan=a,b.options.pan=a;return b};this.setVolume=function(a,e){"undefined"===typeof a&&(a=100);"undefined"===typeof e&&(e=!1);if(b.isHTML5){if(b._a)b._a.volume=Math.max(0,Math.min(1,a/100))}else i._setVolume(b.id,c.muted&&!b.muted||b.muted?0:a);b._iO.volume=a;if(!e)b.volume=a,b.options.volume=a;return b};this.mute=function(){b.muted=!0;if(b.isHTML5){if(b._a)b._a.muted=!0}else i._setVolume(b.id,
0);return b};this.unmute=function(){b.muted=!1;var a="undefined"!==typeof b._iO.volume;if(b.isHTML5){if(b._a)b._a.muted=!1}else i._setVolume(b.id,a?b._iO.volume:b.options.volume);return b};this.toggleMute=function(){return b.muted?b.unmute():b.mute()};this.onposition=this.onPosition=function(a,c,e){k.push({position:parseInt(a,10),method:c,scope:"undefined"!==typeof e?e:b,fired:!1});return b};this.clearOnPosition=function(b,a){var c,b=parseInt(b,10);if(isNaN(b))return!1;for(c=0;c<k.length;c++)if(b===
k[c].position&&(!a||a===k[c].method))k[c].fired&&o--,k.splice(c,1)};this._processOnPosition=function(){var a,c;a=k.length;if(!a||!b.playState||o>=a)return!1;for(a-=1;0<=a;a--)if(c=k[a],!c.fired&&b.position>=c.position)c.fired=!0,o++,c.method.apply(c.scope,[c.position]);return!0};this._resetOnPosition=function(b){var a,c;a=k.length;if(!a)return!1;for(a-=1;0<=a;a--)if(c=k[a],c.fired&&b<=c.position)c.fired=!1,o--;return!0};s=function(){var a=b._iO,c=a.from,e=a.to,d,f;f=function(){b.clearOnPosition(e,
f);b.stop()};d=function(){if(null!==e&&!isNaN(e))b.onPosition(e,f)};if(null!==c&&!isNaN(c))a.position=c,a.multiShot=!1,d();return a};m=function(){var a,c=b._iO.onposition;if(c)for(a in c)if(c.hasOwnProperty(a))b.onPosition(parseInt(a,10),c[a])};q=function(){var a,c=b._iO.onposition;if(c)for(a in c)c.hasOwnProperty(a)&&b.clearOnPosition(parseInt(a,10))};h=function(){b.isHTML5&&Ja(b)};I=function(){b.isHTML5&&Ka(b)};g=function(a){a||(k=[],o=0);l=!1;b._hasTimer=null;b._a=null;b._html5_canplay=!1;b.bytesLoaded=
null;b.bytesTotal=null;b.duration=b._iO&&b._iO.duration?b._iO.duration:null;b.durationEstimate=null;b.buffered=[];b.eqData=[];b.eqData.left=[];b.eqData.right=[];b.failures=0;b.isBuffering=!1;b.instanceOptions={};b.instanceCount=0;b.loaded=!1;b.metadata={};b.readyState=0;b.muted=!1;b.paused=!1;b.peakData={left:0,right:0};b.waveformData={left:[],right:[]};b.playState=0;b.position=null;b.id3={}};g();this._onTimer=function(a){var c,f=!1,g={};if(b._hasTimer||a){if(b._a&&(a||(0<b.playState||1===b.readyState)&&
!b.paused)){c=b._get_html5_duration();if(c!==e)e=c,b.duration=c,f=!0;b.durationEstimate=b.duration;c=1E3*b._a.currentTime||0;c!==d&&(d=c,f=!0);(f||a)&&b._whileplaying(c,g,g,g,g)}return f}};this._get_html5_duration=function(){var a=b._iO;return(a=b._a&&b._a.duration?1E3*b._a.duration:a&&a.duration?a.duration:null)&&!isNaN(a)&&Infinity!==a?a:null};this._apply_loop=function(b,a){b.loop=1<a?"loop":""};this._setup_html5=function(a){var a=r(b._iO,a),e=decodeURI,d=z?c._global_a:b._a,i=e(a.url),h=d&&d._t?
d._t.instanceOptions:null,A;if(d){if(d._t){if(!z&&i===e(n))A=d;else if(z&&h.url===a.url&&(!n||n===h.url))A=d;if(A)return b._apply_loop(d,a.loops),A}z&&d._t&&d._t.playState&&a.url!==h.url&&d._t.stop();g(h&&h.url?a.url===h.url:n?n===a.url:!1);d.src=a.url;n=b.url=a.url;d._called_load=!1}else if(b._a=a.autoLoad||a.autoPlay?new Audio(a.url):ha&&10>opera.version()?new Audio(null):new Audio,d=b._a,d._called_load=!1,z)c._global_a=d;b.isHTML5=!0;b._a=d;d._t=b;f();b._apply_loop(d,a.loops);a.autoLoad||a.autoPlay?
b.load():(d.autobuffer=!1,d.preload="auto");return d};f=function(){if(b._a._added_events)return!1;var a;b._a._added_events=!0;for(a in u)u.hasOwnProperty(a)&&b._a&&b._a.addEventListener(a,u[a],!1);return!0};A=function(){var a;b._a._added_events=!1;for(a in u)u.hasOwnProperty(a)&&b._a&&b._a.removeEventListener(a,u[a],!1)};this._onload=function(a){a=!!a||!b.isHTML5&&8===j&&b.duration;b.loaded=a;b.readyState=a?3:2;b._onbufferchange(0);b._iO.onload&&b._iO.onload.apply(b,[a]);return!0};this._onbufferchange=
function(a){if(0===b.playState||a&&b.isBuffering||!a&&!b.isBuffering)return!1;b.isBuffering=1===a;b._iO.onbufferchange&&b._iO.onbufferchange.apply(b);return!0};this._onsuspend=function(){b._iO.onsuspend&&b._iO.onsuspend.apply(b);return!0};this._onfailure=function(a,c,e){b.failures++;if(b._iO.onfailure&&1===b.failures)b._iO.onfailure(b,a,c,e)};this._onfinish=function(){var a=b._iO.onfinish;b._onbufferchange(0);b._resetOnPosition(0);if(b.instanceCount){b.instanceCount--;if(!b.instanceCount&&(q(),b.playState=
0,b.paused=!1,b.instanceCount=0,b.instanceOptions={},b._iO={},I(),b.isHTML5))b.position=0;(!b.instanceCount||b._iO.multiShotEvents)&&a&&a.apply(b)}};this._whileloading=function(a,c,e,d){var f=b._iO;b.bytesLoaded=a;b.bytesTotal=c;b.duration=Math.floor(e);b.bufferLength=d;b.durationEstimate=!b.isHTML5&&!f.isMovieStar?f.duration?b.duration>f.duration?b.duration:f.duration:parseInt(b.bytesTotal/b.bytesLoaded*b.duration,10):b.duration;if(!b.isHTML5)b.buffered=[{start:0,end:b.duration}];(3!==b.readyState||
b.isHTML5)&&f.whileloading&&f.whileloading.apply(b)};this._whileplaying=function(a,c,e,d,f){var g=b._iO;if(isNaN(a)||null===a)return!1;b.position=Math.max(0,a);b._processOnPosition();if(!b.isHTML5&&8<j){if(g.usePeakData&&"undefined"!==typeof c&&c)b.peakData={left:c.leftPeak,right:c.rightPeak};if(g.useWaveformData&&"undefined"!==typeof e&&e)b.waveformData={left:e.split(","),right:d.split(",")};if(g.useEQData&&"undefined"!==typeof f&&f&&f.leftEQ&&(a=f.leftEQ.split(","),b.eqData=a,b.eqData.left=a,"undefined"!==
typeof f.rightEQ&&f.rightEQ))b.eqData.right=f.rightEQ.split(",")}1===b.playState&&(!b.isHTML5&&8===j&&!b.position&&b.isBuffering&&b._onbufferchange(0),g.whileplaying&&g.whileplaying.apply(b));return!0};this._oncaptiondata=function(a){b.captiondata=a;b._iO.oncaptiondata&&b._iO.oncaptiondata.apply(b,[a])};this._onmetadata=function(a,c){var e={},d,f;for(d=0,f=a.length;d<f;d++)e[a[d]]=c[d];b.metadata=e;b._iO.onmetadata&&b._iO.onmetadata.apply(b)};this._onid3=function(a,c){var e=[],d,f;for(d=0,f=a.length;d<
f;d++)e[a[d]]=c[d];b.id3=r(b.id3,e);b._iO.onid3&&b._iO.onid3.apply(b)};this._onconnect=function(a){a=1===a;if(b.connected=a)b.failures=0,p(b.id)&&(b.getAutoPlay()?b.play(void 0,b.getAutoPlay()):b._iO.autoLoad&&b.load()),b._iO.onconnect&&b._iO.onconnect.apply(b,[a])};this._ondataerror=function(){0<b.playState&&b._iO.ondataerror&&b._iO.ondataerror.apply(b)}};qa=function(){return m.body||m._docElement||m.getElementsByTagName("div")[0]};T=function(a){return m.getElementById(a)};r=function(a,e){var d=
a||{},b,g;b="undefined"===typeof e?c.defaultOptions:e;for(g in b)b.hasOwnProperty(g)&&"undefined"===typeof d[g]&&(d[g]="object"!==typeof b[g]||null===b[g]?b[g]:r(d[g],b[g]));return d};U={onready:1,ontimeout:1,defaultOptions:1,flash9Options:1,movieStarOptions:1};ma=function(a,e){var d,b=!0,g="undefined"!==typeof e,f=c.setupOptions;for(d in a)if(a.hasOwnProperty(d))if("object"!==typeof a[d]||null===a[d]||a[d]instanceof Array)g&&"undefined"!==typeof U[e]?c[e][d]=a[d]:"undefined"!==typeof f[d]?(c.setupOptions[d]=
a[d],c[d]=a[d]):"undefined"===typeof U[d]?(H(t("undefined"===typeof c[d]?"setupUndef":"setupError",d),2),b=!1):c[d]instanceof Function?c[d].apply(c,a[d]instanceof Array?a[d]:[a[d]]):c[d]=a[d];else if("undefined"===typeof U[d])H(t("undefined"===typeof c[d]?"setupUndef":"setupError",d),2),b=!1;else return ma(a[d],d);return b};o=function(){function a(a){var a=Wa.call(a),b=a.length;d?(a[1]="on"+a[1],3<b&&a.pop()):3===b&&a.push(!1);return a}function c(a,e){var h=a.shift(),i=[b[e]];if(d)h[i](a[0],a[1]);
else h[i].apply(h,a)}var d=h.attachEvent,b={add:d?"attachEvent":"addEventListener",remove:d?"detachEvent":"removeEventListener"};return{add:function(){c(a(arguments),"add")},remove:function(){c(a(arguments),"remove")}}}();u={abort:l(function(){}),canplay:l(function(){var a=this._t,c;if(a._html5_canplay)return!0;a._html5_canplay=!0;a._onbufferchange(0);c="undefined"!==typeof a._iO.position&&!isNaN(a._iO.position)?a._iO.position/1E3:null;if(a.position&&this.currentTime!==c)try{this.currentTime=c}catch(d){}a._iO._oncanplay&&
a._iO._oncanplay()}),canplaythrough:l(function(){var a=this._t;a.loaded||(a._onbufferchange(0),a._whileloading(a.bytesLoaded,a.bytesTotal,a._get_html5_duration()),a._onload(!0))}),ended:l(function(){this._t._onfinish()}),error:l(function(){this._t._onload(!1)}),loadeddata:l(function(){var a=this._t;if(!a._loaded&&!za)a.duration=a._get_html5_duration()}),loadedmetadata:l(function(){}),loadstart:l(function(){this._t._onbufferchange(1)}),play:l(function(){this._t._onbufferchange(0)}),playing:l(function(){this._t._onbufferchange(0)}),
progress:l(function(a){var c=this._t,d,b,g=0,g=a.target.buffered;d=a.loaded||0;var f=a.total||1;c.buffered=[];if(g&&g.length){for(d=0,b=g.length;d<b;d++)c.buffered.push({start:1E3*g.start(d),end:1E3*g.end(d)});g=1E3*(g.end(0)-g.start(0));d=g/(1E3*a.target.duration)}isNaN(d)||(c._onbufferchange(0),c._whileloading(d,f,c._get_html5_duration()),d&&f&&d===f&&u.canplaythrough.call(this,a))}),ratechange:l(function(){}),suspend:l(function(a){var c=this._t;u.progress.call(this,a);c._onsuspend()}),stalled:l(function(){}),
timeupdate:l(function(){this._t._onTimer()}),waiting:l(function(){this._t._onbufferchange(1)})};ca=function(a){return a.serverURL||a.type&&S(a.type)?!1:a.type?Q({type:a.type}):Q({url:a.url})||c.html5Only};va=function(a,c){if(a)a.src=c};Q=function(a){if(!c.useHTML5Audio||!c.hasHTML5)return!1;var e=a.url||null,a=a.type||null,d=c.audioFormats,b;if(a&&"undefined"!==typeof c.html5[a])return c.html5[a]&&!S(a);if(!w){w=[];for(b in d)d.hasOwnProperty(b)&&(w.push(b),d[b].related&&(w=w.concat(d[b].related)));
w=RegExp("\\.("+w.join("|")+")(\\?.*)?$","i")}b=e?e.toLowerCase().match(w):null;!b||!b.length?a&&(e=a.indexOf(";"),b=(-1!==e?a.substr(0,e):a).substr(6)):b=b[1];b&&"undefined"!==typeof c.html5[b]?e=c.html5[b]&&!S(b):(a="audio/"+b,e=c.html5.canPlayType({type:a}),e=(c.html5[b]=e)&&c.html5[a]&&!S(a));return e};Na=function(){function a(a){var b,d,f=b=!1;if(!e||"function"!==typeof e.canPlayType)return b;if(a instanceof Array){for(b=0,d=a.length;b<d;b++)if(c.html5[a[b]]||e.canPlayType(a[b]).match(c.html5Test))f=
!0,c.html5[a[b]]=!0,c.flash[a[b]]=!!a[b].match(Sa);b=f}else a=e&&"function"===typeof e.canPlayType?e.canPlayType(a):!1,b=!(!a||!a.match(c.html5Test));return b}if(!c.useHTML5Audio||!c.hasHTML5)return!1;var e="undefined"!==typeof Audio?ha&&10>opera.version()?new Audio(null):new Audio:null,d,b,g={},f;f=c.audioFormats;for(d in f)if(f.hasOwnProperty(d)&&(b="audio/"+d,g[d]=a(f[d].type),g[b]=g[d],d.match(Sa)?(c.flash[d]=!0,c.flash[b]=!0):(c.flash[d]=!1,c.flash[b]=!1),f[d]&&f[d].related))for(b=f[d].related.length-
1;0<=b;b--)g["audio/"+f[d].related[b]]=g[d],c.html5[f[d].related[b]]=g[d],c.flash[f[d].related[b]]=g[d];g.canPlayType=e?a:null;c.html5=r(c.html5,g);return!0};t=function(){};Z=function(a){if(8===j&&1<a.loops&&a.stream)a.stream=!1;return a};$=function(a){if(a&&!a.usePolicyFile&&(a.onid3||a.usePeakData||a.useWaveformData||a.useEQData))a.usePolicyFile=!0;return a};H=function(){};ja=function(){return!1};Ha=function(a){for(var c in a)a.hasOwnProperty(c)&&"function"===typeof a[c]&&(a[c]=ja)};Y=function(a){"undefined"===
typeof a&&(a=!1);(s||a)&&c.disable(a)};Ia=function(a){var e=null;if(a)if(a.match(/\.swf(\?.*)?$/i)){if(e=a.substr(a.toLowerCase().lastIndexOf(".swf?")+4))return a}else a.lastIndexOf("/")!==a.length-1&&(a+="/");a=(a&&-1!==a.lastIndexOf("/")?a.substr(0,a.lastIndexOf("/")+1):"./")+c.movieURL;c.noSWFCache&&(a+="?ts="+(new Date).getTime());return a};oa=function(){j=parseInt(c.flashVersion,10);if(8!==j&&9!==j)c.flashVersion=j=8;var a=c.debugMode||c.debugFlash?"_debug.swf":".swf";if(c.useHTML5Audio&&!c.html5Only&&
c.audioFormats.mp4.required&&9>j)c.flashVersion=j=9;c.version=c.versionNumber+(c.html5Only?" (HTML5-only mode)":9===j?" (AS3/Flash 9)":" (AS2/Flash 8)");8<j?(c.defaultOptions=r(c.defaultOptions,c.flash9Options),c.features.buffering=!0,c.defaultOptions=r(c.defaultOptions,c.movieStarOptions),c.filePatterns.flash9=RegExp("\\.(mp3|"+Va.join("|")+")(\\?.*)?$","i"),c.features.movieStar=!0):c.features.movieStar=!1;c.filePattern=c.filePatterns[8!==j?"flash9":"flash8"];c.movieURL=(8===j?"soundmanager2.swf":
"soundmanager2_flash9.swf").replace(".swf",a);c.features.peakData=c.features.waveformData=c.features.eqData=8<j};Ga=function(a,c){if(!i)return!1;i._setPolling(a,c)};ra=function(){if(c.debugURLParam.test(ia))c.debugMode=!0};p=this.getSoundById;G=function(){var a=[];c.debugMode&&a.push("sm2_debug");c.debugFlash&&a.push("flash_debug");c.useHighPerformance&&a.push("high_performance");return a.join(" ")};ta=function(){t("fbHandler");var a=c.getMoviePercent(),e={type:"FLASHBLOCK"};if(c.html5Only)return!1;
if(c.ok()){if(c.oMC)c.oMC.className=[G(),"movieContainer","swf_loaded"+(c.didFlashBlock?" swf_unblocked":"")].join(" ")}else{if(n)c.oMC.className=G()+" movieContainer "+(null===a?"swf_timedout":"swf_error");c.didFlashBlock=!0;B({type:"ontimeout",ignoreInit:!0,error:e});F(e)}};na=function(a,c,d){"undefined"===typeof v[a]&&(v[a]=[]);v[a].push({method:c,scope:d||null,fired:!1})};B=function(a){a||(a={type:c.ok()?"onready":"ontimeout"});if(!k&&a&&!a.ignoreInit||"ontimeout"===a.type&&(c.ok()||s&&!a.ignoreInit))return!1;
var e={success:a&&a.ignoreInit?c.ok():!s},d=a&&a.type?v[a.type]||[]:[],b=[],g,e=[e],f=n&&c.useFlashBlock&&!c.ok();if(a.error)e[0].error=a.error;for(a=0,g=d.length;a<g;a++)!0!==d[a].fired&&b.push(d[a]);if(b.length)for(a=0,g=b.length;a<g;a++)if(b[a].scope?b[a].method.apply(b[a].scope,e):b[a].method.apply(this,e),!f)b[a].fired=!0;return!0};C=function(){h.setTimeout(function(){c.useFlashBlock&&ta();B();"function"===typeof c.onload&&c.onload.apply(h);c.waitForWindowLoad&&o.add(h,"load",C)},1)};xa=function(){if("undefined"!==
typeof y)return y;var a=!1,c=navigator,d=c.plugins,b,g=h.ActiveXObject;if(d&&d.length)(c=c.mimeTypes)&&c["application/x-shockwave-flash"]&&c["application/x-shockwave-flash"].enabledPlugin&&c["application/x-shockwave-flash"].enabledPlugin.description&&(a=!0);else if("undefined"!==typeof g){try{b=new g("ShockwaveFlash.ShockwaveFlash")}catch(f){}a=!!b}return y=a};Ma=function(){var a,e,d=c.audioFormats;if(ya&&q.match(/os (1|2|3_0|3_1)/i)){if(c.hasHTML5=!1,c.html5Only=!0,c.oMC)c.oMC.style.display="none"}else if(c.useHTML5Audio&&
(!c.html5||!c.html5.canPlayType))c.hasHTML5=!1;if(c.useHTML5Audio&&c.hasHTML5)for(e in d)if(d.hasOwnProperty(e)&&(d[e].required&&!c.html5.canPlayType(d[e].type)||c.preferFlash&&(c.flash[e]||c.flash[d[e].type])))a=!0;c.ignoreFlash&&(a=!1);c.html5Only=c.hasHTML5&&c.useHTML5Audio&&!a;return!c.html5Only};ba=function(a){var e,d,b=0;if(a instanceof Array){for(e=0,d=a.length;e<d;e++)if(a[e]instanceof Object){if(c.canPlayMIME(a[e].type)){b=e;break}}else if(c.canPlayURL(a[e])){b=e;break}if(a[b].url)a[b]=a[b].url;
a=a[b]}return a};Ja=function(a){if(!a._hasTimer)a._hasTimer=!0,!Aa&&c.html5PollingInterval&&(null===P&&0===aa&&(P=h.setInterval(La,c.html5PollingInterval)),aa++)};Ka=function(a){if(a._hasTimer)a._hasTimer=!1,!Aa&&c.html5PollingInterval&&aa--};La=function(){var a;if(null!==P&&!aa)return h.clearInterval(P),P=null,!1;for(a=c.soundIDs.length-1;0<=a;a--)c.sounds[c.soundIDs[a]].isHTML5&&c.sounds[c.soundIDs[a]]._hasTimer&&c.sounds[c.soundIDs[a]]._onTimer()};F=function(a){a="undefined"!==typeof a?a:{};"function"===
typeof c.onerror&&c.onerror.apply(h,[{type:"undefined"!==typeof a.type?a.type:null}]);"undefined"!==typeof a.fatal&&a.fatal&&c.disable()};Oa=function(){if(!Qa||!xa())return!1;var a=c.audioFormats,e,d;for(d in a)if(a.hasOwnProperty(d)&&("mp3"===d||"mp4"===d))if(c.html5[d]=!1,a[d]&&a[d].related)for(e=a[d].related.length-1;0<=e;e--)c.html5[a[d].related[e]]=!1};this._setSandboxType=function(){};this._externalInterfaceOK=function(){if(c.swfLoaded)return!1;(new Date).getTime();c.swfLoaded=!0;da=!1;Qa&&
Oa();setTimeout(ka,x?100:1)};X=function(a,e){function d(a,b){return'<param name="'+a+'" value="'+b+'" />'}if(J&&K)return!1;if(c.html5Only)return oa(),c.oMC=T(c.movieID),ka(),K=J=!0,!1;var b=e||c.url,g=c.altURL||b,f=qa(),h=G(),i=null,i=m.getElementsByTagName("html")[0],j,k,l,i=i&&i.dir&&i.dir.match(/rtl/i),a="undefined"===typeof a?c.id:a;oa();c.url=Ia(Ca?b:g);e=c.url;c.wmode=!c.wmode&&c.useHighPerformance?"transparent":c.wmode;if(null!==c.wmode&&(q.match(/msie 8/i)||!x&&!c.useHighPerformance)&&navigator.platform.match(/win32|win64/i))c.wmode=
null;f={name:a,id:a,src:e,quality:"high",allowScriptAccess:c.allowScriptAccess,bgcolor:c.bgColor,pluginspage:Ta+"www.macromedia.com/go/getflashplayer",title:"JS/Flash audio component (SoundManager 2)",type:"application/x-shockwave-flash",wmode:c.wmode,hasPriority:"true"};if(c.debugFlash)f.FlashVars="debug=1";c.wmode||delete f.wmode;if(x)b=m.createElement("div"),k=['<object id="'+a+'" data="'+e+'" type="'+f.type+'" title="'+f.title+'" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="'+
Ta+'download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0">',d("movie",e),d("AllowScriptAccess",c.allowScriptAccess),d("quality",f.quality),c.wmode?d("wmode",c.wmode):"",d("bgcolor",c.bgColor),d("hasPriority","true"),c.debugFlash?d("FlashVars",f.FlashVars):"","</object>"].join("");else for(j in b=m.createElement("embed"),f)f.hasOwnProperty(j)&&b.setAttribute(j,f[j]);ra();h=G();if(f=qa())if(c.oMC=T(c.movieID)||m.createElement("div"),c.oMC.id){l=c.oMC.className;c.oMC.className=
(l?l+" ":"movieContainer")+(h?" "+h:"");c.oMC.appendChild(b);if(x)j=c.oMC.appendChild(m.createElement("div")),j.className="sm2-object-box",j.innerHTML=k;K=!0}else{c.oMC.id=c.movieID;c.oMC.className="movieContainer "+h;j=h=null;if(!c.useFlashBlock)if(c.useHighPerformance)h={position:"fixed",width:"8px",height:"8px",bottom:"0px",left:"0px",overflow:"hidden"};else if(h={position:"absolute",width:"6px",height:"6px",top:"-9999px",left:"-9999px"},i)h.left=Math.abs(parseInt(h.left,10))+"px";if(Xa)c.oMC.style.zIndex=
1E4;if(!c.debugFlash)for(l in h)h.hasOwnProperty(l)&&(c.oMC.style[l]=h[l]);try{x||c.oMC.appendChild(b);f.appendChild(c.oMC);if(x)j=c.oMC.appendChild(m.createElement("div")),j.className="sm2-object-box",j.innerHTML=k;K=!0}catch(n){throw Error(t("domError")+" \n"+n.toString());}}return J=!0};W=function(){if(c.html5Only)return X(),!1;if(i||!c.url)return!1;i=c.getMovie(c.id);if(!i)N?(x?c.oMC.innerHTML=sa:c.oMC.appendChild(N),N=null,J=!0):X(c.id,c.url),i=c.getMovie(c.id);"function"===typeof c.oninitmovie&&
setTimeout(c.oninitmovie,1);return!0};D=function(){setTimeout(Fa,1E3)};Fa=function(){var a,e=!1;if(!c.url||O)return!1;O=!0;o.remove(h,"load",D);if(da&&!Ba)return!1;k||(a=c.getMoviePercent(),0<a&&100>a&&(e=!0));setTimeout(function(){a=c.getMoviePercent();if(e)return O=!1,h.setTimeout(D,1),!1;!k&&Ra&&(null===a?c.useFlashBlock||0===c.flashLoadTimeout?c.useFlashBlock&&ta():Y(!0):0!==c.flashLoadTimeout&&Y(!0))},c.flashLoadTimeout)};V=function(){if(Ba||!da)return o.remove(h,"focus",V),!0;Ba=Ra=!0;O=!1;
D();o.remove(h,"focus",V);return!0};Pa=function(){};L=function(a){if(k)return!1;if(c.html5Only)return k=!0,C(),!0;var e=!0,d;if(!c.useFlashBlock||!c.flashLoadTimeout||c.getMoviePercent())k=!0,s&&(d={type:!y&&n?"NO_FLASH":"INIT_TIMEOUT"});if(s||a){if(c.useFlashBlock&&c.oMC)c.oMC.className=G()+" "+(null===c.getMoviePercent()?"swf_timedout":"swf_error");B({type:"ontimeout",error:d,ignoreInit:!0});F(d);e=!1}s||(c.waitForWindowLoad&&!la?o.add(h,"load",C):C());return e};Ea=function(){var a,e=c.setupOptions;
for(a in e)e.hasOwnProperty(a)&&("undefined"===typeof c[a]?c[a]=e[a]:c[a]!==e[a]&&(c.setupOptions[a]=c[a]))};ka=function(){if(k)return!1;if(c.html5Only){if(!k)o.remove(h,"load",c.beginDelayedInit),c.enabled=!0,L();return!0}W();try{i._externalInterfaceTest(!1),Ga(!0,c.flashPollingInterval||(c.useHighPerformance?10:50)),c.debugMode||i._disableDebug(),c.enabled=!0,c.html5Only||o.add(h,"unload",ja)}catch(a){return F({type:"JS_TO_FLASH_EXCEPTION",fatal:!0}),Y(!0),L(),!1}L();o.remove(h,"load",c.beginDelayedInit);
return!0};E=function(){if(M)return!1;M=!0;Ea();ra();!y&&c.hasHTML5&&c.setup({useHTML5Audio:!0,preferFlash:!1});Na();c.html5.usingFlash=Ma();n=c.html5.usingFlash;Pa();!y&&n&&c.setup({flashLoadTimeout:1});m.removeEventListener&&m.removeEventListener("DOMContentLoaded",E,!1);W();return!0};wa=function(){"complete"===m.readyState&&(E(),m.detachEvent("onreadystatechange",wa));return!0};pa=function(){la=!0;o.remove(h,"load",pa)};xa();o.add(h,"focus",V);o.add(h,"load",D);o.add(h,"load",pa);m.addEventListener?
m.addEventListener("DOMContentLoaded",E,!1):m.attachEvent?m.attachEvent("onreadystatechange",wa):F({type:"NO_DOM2_EVENTS",fatal:!0})}var ea=null;if("undefined"===typeof SM2_DEFER||!SM2_DEFER)ea=new R;fa.SoundManager=R;fa.soundManager=ea})(window);
/** @license
	Animator.js 1.1.9
	
	This library is released under the BSD license:

	Copyright (c) 2006, Bernard Sumption. All rights reserved.
	
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:
	
	Redistributions of source code must retain the above copyright notice, this
	list of conditions and the following disclaimer. Redistributions in binary
	form must reproduce the above copyright notice, this list of conditions and
	the following disclaimer in the documentation and/or other materials
	provided with the distribution. Neither the name BernieCode nor
	the names of its contributors may be used to endorse or promote products
	derived from this software without specific prior written permission. 
	
	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
	AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
	IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
	ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
	ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
	DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
	SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
	CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
	LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
	OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
	DAMAGE.

*/

// http://www.berniecode.com/writing/animator.html

// Applies a sequence of numbers between 0 and 1 to a number of subjects
// construct - see setOptions for parameters
function Animator(options) {
	this.setOptions(options);
	var _this = this;
	this.timerDelegate = function(){_this.onTimerEvent()};
	this.subjects = [];
	this.subjectScopes = [];
	this.target = 0;
	this.state = 0;
	this.lastTime = null;
};
Animator.prototype = {
	// apply defaults
	setOptions: function(options) {
		this.options = Animator.applyDefaults({
			interval: 20,  // time between animation frames
			duration: 400, // length of animation
			onComplete: function(){},
			onStep: function(){},
			transition: Animator.tx.easeInOut
		}, options);
	},
	// animate from the current state to provided value
	seekTo: function(to) {
		this.seekFromTo(this.state, to);
	},
	// animate from the current state to provided value
	seekFromTo: function(from, to) {
		this.target = Math.max(0, Math.min(1, to));
		this.state = Math.max(0, Math.min(1, from));
		this.lastTime = new Date().getTime();
		if (!this.intervalId) {
			this.intervalId = window.setInterval(this.timerDelegate, this.options.interval);
		}
	},
	// animate from the current state to provided value
	jumpTo: function(to) {
		this.target = this.state = Math.max(0, Math.min(1, to));
		this.propagate();
	},
	// seek to the opposite of the current target
	toggle: function() {
		this.seekTo(1 - this.target);
	},
	// add a function or an object with a method setState(state) that will be called with a number
	// between 0 and 1 on each frame of the animation
	addSubject: function(subject,scope) {
		this.subjects[this.subjects.length] = subject;
		this.subjectScopes[this.subjectScopes.length] = scope;
		return this;
	},
	// remove all subjects
	clearSubjects: function() {
		this.subjects = [];
		this.subjectScopes = [];
	},
	// forward the current state to the animation subjects
	propagate: function() {
		var value = this.options.transition(this.state);
		for (var i=0; i<this.subjects.length; i++) {
			if (this.subjects[i].setState) {
				this.subjects[i].setState(value);
			} else {
				this.subjects[i].apply(this.subjectScopes[i],[value]);
			}
		}
	},
	// called once per frame to update the current state
	onTimerEvent: function() {
		var now = new Date().getTime();
		var timePassed = now - this.lastTime;
		this.lastTime = now;
		var movement = (timePassed / this.options.duration) * (this.state < this.target ? 1 : -1);
		if (Math.abs(movement) >= Math.abs(this.state - this.target)) {
			this.state = this.target;
		} else {
			this.state += movement;
		}
		
		try {
			this.propagate();
		} finally {
			this.options.onStep.call(this);
			if (this.target == this.state) {
				window.clearInterval(this.intervalId);
				this.intervalId = null;
				this.options.onComplete.call(this);
			}
		}
	},
	// shortcuts
	play: function() {this.seekFromTo(0, 1)},
	reverse: function() {this.seekFromTo(1, 0)},
	// return a string describing this Animator, for debugging
	inspect: function() {
		var str = "#<Animator:\n";
		for (var i=0; i<this.subjects.length; i++) {
			str += this.subjects[i].inspect();
		}
		str += ">";
		return str;
	}
}
// merge the properties of two objects
Animator.applyDefaults = function(defaults, prefs) {
	prefs = prefs || {};
	var prop, result = {};
	for (prop in defaults) result[prop] = prefs[prop] !== undefined ? prefs[prop] : defaults[prop];
	return result;
}
// make an array from any object
Animator.makeArray = function(o) {
	if (o == null) return [];
	if (!o.length) return [o];
	var result = [];
	for (var i=0; i<o.length; i++) result[i] = o[i];
	return result;
}
// convert a dash-delimited-property to a camelCaseProperty (c/o Prototype, thanks Sam!)
Animator.camelize = function(string) {
	var oStringList = string.split('-');
	if (oStringList.length == 1) return oStringList[0];
	
	var camelizedString = string.indexOf('-') == 0
		? oStringList[0].charAt(0).toUpperCase() + oStringList[0].substring(1)
		: oStringList[0];
	
	for (var i = 1, len = oStringList.length; i < len; i++) {
		var s = oStringList[i];
		camelizedString += s.charAt(0).toUpperCase() + s.substring(1);
	}
	return camelizedString;
}
// syntactic sugar for creating CSSStyleSubjects
Animator.apply = function(el, style, options) {
	if (style instanceof Array) {
		return new Animator(options).addSubject(new CSSStyleSubject(el, style[0], style[1]));
	}
	return new Animator(options).addSubject(new CSSStyleSubject(el, style));
}
// make a transition function that gradually accelerates. pass a=1 for smooth
// gravitational acceleration, higher values for an exaggerated effect
Animator.makeEaseIn = function(a) {
	return function(state) {
		return Math.pow(state, a*2); 
	}
}
// as makeEaseIn but for deceleration
Animator.makeEaseOut = function(a) {
	return function(state) {
		return 1 - Math.pow(1 - state, a*2); 
	}
}
// make a transition function that, like an object with momentum being attracted to a point,
// goes past the target then returns
Animator.makeElastic = function(bounces) {
	return function(state) {
		state = Animator.tx.easeInOut(state);
		return ((1-Math.cos(state * Math.PI * bounces)) * (1 - state)) + state; 
	}
}
// make an Attack Decay Sustain Release envelope that starts and finishes on the same level
// 
Animator.makeADSR = function(attackEnd, decayEnd, sustainEnd, sustainLevel) {
	if (sustainLevel == null) sustainLevel = 0.5;
	return function(state) {
		if (state < attackEnd) {
			return state / attackEnd;
		}
		if (state < decayEnd) {
			return 1 - ((state - attackEnd) / (decayEnd - attackEnd) * (1 - sustainLevel));
		}
		if (state < sustainEnd) {
			return sustainLevel;
		}
		return sustainLevel * (1 - ((state - sustainEnd) / (1 - sustainEnd)));
	}
}
// make a transition function that, like a ball falling to floor, reaches the target and/
// bounces back again
Animator.makeBounce = function(bounces) {
	var fn = Animator.makeElastic(bounces);
	return function(state) {
		state = fn(state); 
		return state <= 1 ? state : 2-state;
	}
}
 
// pre-made transition functions to use with the 'transition' option
Animator.tx = {
	easeInOut: function(pos){
		return ((-Math.cos(pos*Math.PI)/2) + 0.5);
	},
	linear: function(x) {
		return x;
	},
	easeIn: Animator.makeEaseIn(1.5),
	easeOut: Animator.makeEaseOut(1.5),
	strongEaseIn: Animator.makeEaseIn(2.5),
	strongEaseOut: Animator.makeEaseOut(2.5),
	elastic: Animator.makeElastic(1),
	veryElastic: Animator.makeElastic(3),
	bouncy: Animator.makeBounce(1),
	veryBouncy: Animator.makeBounce(3)
}

// animates a pixel-based style property between two integer values
function NumericalStyleSubject(els, property, from, to, units) {
	this.els = Animator.makeArray(els);
	if (property == 'opacity' && window.ActiveXObject) {
		this.property = 'filter';
	} else {
		this.property = Animator.camelize(property);
	}
	this.from = parseFloat(from);
	this.to = parseFloat(to);
	this.units = units != null ? units : 'px';
}
NumericalStyleSubject.prototype = {
	setState: function(state) {
		var style = this.getStyle(state);
		var visibility = (this.property == 'opacity' && state == 0) ? 'hidden' : '';
		var j=0;
		for (var i=0; i<this.els.length; i++) {
			try {
				this.els[i].style[this.property] = style;
			} catch (e) {
				// ignore fontWeight - intermediate numerical values cause exeptions in firefox
				if (this.property != 'fontWeight') throw e;
			}
			if (j++ > 20) return;
		}
	},
	getStyle: function(state) {
		state = this.from + ((this.to - this.from) * state);
		if (this.property == 'filter') return "alpha(opacity=" + Math.round(state*100) + ")";
		if (this.property == 'opacity') return state;
		return Math.round(state) + this.units;
	},
	inspect: function() {
		return "\t" + this.property + "(" + this.from + this.units + " to " + this.to + this.units + ")\n";
	}
}

// animates a colour based style property between two hex values
function ColorStyleSubject(els, property, from, to) {
	this.els = Animator.makeArray(els);
	this.property = Animator.camelize(property);
	this.to = this.expandColor(to);
	this.from = this.expandColor(from);
	this.origFrom = from;
	this.origTo = to;
}

ColorStyleSubject.prototype = {
	// parse "#FFFF00" to [256, 256, 0]
	expandColor: function(color) {
		var hexColor, red, green, blue;
		hexColor = ColorStyleSubject.parseColor(color);
		if (hexColor) {
			red = parseInt(hexColor.slice(1, 3), 16);
			green = parseInt(hexColor.slice(3, 5), 16);
			blue = parseInt(hexColor.slice(5, 7), 16);
			return [red,green,blue]
		}
		if (window.DEBUG) {
			alert("Invalid colour: '" + color + "'");
		}
	},
	getValueForState: function(color, state) {
		return Math.round(this.from[color] + ((this.to[color] - this.from[color]) * state));
	},
	setState: function(state) {
		var color = '#'
				+ ColorStyleSubject.toColorPart(this.getValueForState(0, state))
				+ ColorStyleSubject.toColorPart(this.getValueForState(1, state))
				+ ColorStyleSubject.toColorPart(this.getValueForState(2, state));
		for (var i=0; i<this.els.length; i++) {
			this.els[i].style[this.property] = color;
		}
	},
	inspect: function() {
		return "\t" + this.property + "(" + this.origFrom + " to " + this.origTo + ")\n";
	}
}

// return a properly formatted 6-digit hex colour spec, or false
ColorStyleSubject.parseColor = function(string) {
	var color = '#', match;
	if(match = ColorStyleSubject.parseColor.rgbRe.exec(string)) {
		var part;
		for (var i=1; i<=3; i++) {
			part = Math.max(0, Math.min(255, parseInt(match[i])));
			color += ColorStyleSubject.toColorPart(part);
		}
		return color;
	}
	if (match = ColorStyleSubject.parseColor.hexRe.exec(string)) {
		if(match[1].length == 3) {
			for (var i=0; i<3; i++) {
				color += match[1].charAt(i) + match[1].charAt(i);
			}
			return color;
		}
		return '#' + match[1];
	}
	return false;
}
// convert a number to a 2 digit hex string
ColorStyleSubject.toColorPart = function(number) {
	if (number > 255) number = 255;
	var digits = number.toString(16);
	if (number < 16) return '0' + digits;
	return digits;
}
ColorStyleSubject.parseColor.rgbRe = /^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/i;
ColorStyleSubject.parseColor.hexRe = /^\#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/;

// Animates discrete styles, i.e. ones that do not scale but have discrete values
// that can't be interpolated
function DiscreteStyleSubject(els, property, from, to, threshold) {
	this.els = Animator.makeArray(els);
	this.property = Animator.camelize(property);
	this.from = from;
	this.to = to;
	this.threshold = threshold || 0.5;
}

DiscreteStyleSubject.prototype = {
	setState: function(state) {
		var j=0;
		for (var i=0; i<this.els.length; i++) {
			this.els[i].style[this.property] = state <= this.threshold ? this.from : this.to; 
		}
	},
	inspect: function() {
		return "\t" + this.property + "(" + this.from + " to " + this.to + " @ " + this.threshold + ")\n";
	}
}

// animates between two styles defined using CSS.
// if style1 and style2 are present, animate between them, if only style1
// is present, animate between the element's current style and style1
function CSSStyleSubject(els, style1, style2) {
	els = Animator.makeArray(els);
	this.subjects = [];
	if (els.length == 0) return;
	var prop, toStyle, fromStyle;
	if (style2) {
		fromStyle = this.parseStyle(style1, els[0]);
		toStyle = this.parseStyle(style2, els[0]);
	} else {
		toStyle = this.parseStyle(style1, els[0]);
		fromStyle = {};
		for (prop in toStyle) {
			fromStyle[prop] = CSSStyleSubject.getStyle(els[0], prop);
		}
	}
	// remove unchanging properties
	var prop;
	for (prop in fromStyle) {
		if (fromStyle[prop] == toStyle[prop]) {
			delete fromStyle[prop];
			delete toStyle[prop];
		}
	}
	// discover the type (numerical or colour) of each style
	var prop, units, match, type, from, to;
	for (prop in fromStyle) {
		var fromProp = String(fromStyle[prop]);
		var toProp = String(toStyle[prop]);
		if (toStyle[prop] == null) {
			if (window.DEBUG) alert("No to style provided for '" + prop + '"');
			continue;
		}
		
		if (from = ColorStyleSubject.parseColor(fromProp)) {
			to = ColorStyleSubject.parseColor(toProp);
			type = ColorStyleSubject;
		} else if (fromProp.match(CSSStyleSubject.numericalRe)
				&& toProp.match(CSSStyleSubject.numericalRe)) {
			from = parseFloat(fromProp);
			to = parseFloat(toProp);
			type = NumericalStyleSubject;
			match = CSSStyleSubject.numericalRe.exec(fromProp);
			var reResult = CSSStyleSubject.numericalRe.exec(toProp);
			if (match[1] != null) {
				units = match[1];
			} else if (reResult[1] != null) {
				units = reResult[1];
			} else {
				units = reResult;
			}
		} else if (fromProp.match(CSSStyleSubject.discreteRe)
				&& toProp.match(CSSStyleSubject.discreteRe)) {
			from = fromProp;
			to = toProp;
			type = DiscreteStyleSubject;
			units = 0;   // hack - how to get an animator option down to here
		} else {
			if (window.DEBUG) {
				alert("Unrecognised format for value of "
					+ prop + ": '" + fromStyle[prop] + "'");
			}
			continue;
		}
		this.subjects[this.subjects.length] = new type(els, prop, from, to, units);
	}
}

CSSStyleSubject.prototype = {
	// parses "width: 400px; color: #FFBB2E" to {width: "400px", color: "#FFBB2E"}
	parseStyle: function(style, el) {
		var rtn = {};
		// if style is a rule set
		if (style.indexOf(":") != -1) {
			var styles = style.split(";");
			for (var i=0; i<styles.length; i++) {
				var parts = CSSStyleSubject.ruleRe.exec(styles[i]);
				if (parts) {
					rtn[parts[1]] = parts[2];
				}
			}
		}
		// else assume style is a class name
		else {
			var prop, value, oldClass;
			oldClass = el.className;
			el.className = style;
			for (var i=0; i<CSSStyleSubject.cssProperties.length; i++) {
				prop = CSSStyleSubject.cssProperties[i];
				value = CSSStyleSubject.getStyle(el, prop);
				if (value != null) {
					rtn[prop] = value;
				}
			}
			el.className = oldClass;
		}
		return rtn;
		
	},
	setState: function(state) {
		for (var i=0; i<this.subjects.length; i++) {
			this.subjects[i].setState(state);
		}
	},
	inspect: function() {
		var str = "";
		for (var i=0; i<this.subjects.length; i++) {
			str += this.subjects[i].inspect();
		}
		return str;
	}
}
// get the current value of a css property, 
CSSStyleSubject.getStyle = function(el, property){
	var style;
	if(document.defaultView && document.defaultView.getComputedStyle){
		style = document.defaultView.getComputedStyle(el, "").getPropertyValue(property);
		if (style) {
			return style;
		}
	}
	property = Animator.camelize(property);
	if(el.currentStyle){
		style = el.currentStyle[property];
	}
	return style || el.style[property]
}


CSSStyleSubject.ruleRe = /^\s*([a-zA-Z\-]+)\s*:\s*(\S(.+\S)?)\s*$/;
CSSStyleSubject.numericalRe = /^-?\d+(?:\.\d+)?(%|[a-zA-Z]{2})?$/;
CSSStyleSubject.discreteRe = /^\w+$/;

// required because the style object of elements isn't enumerable in Safari
/*
CSSStyleSubject.cssProperties = ['background-color','border','border-color','border-spacing',
'border-style','border-top','border-right','border-bottom','border-left','border-top-color',
'border-right-color','border-bottom-color','border-left-color','border-top-width','border-right-width',
'border-bottom-width','border-left-width','border-width','bottom','color','font-size','font-size-adjust',
'font-stretch','font-style','height','left','letter-spacing','line-height','margin','margin-top',
'margin-right','margin-bottom','margin-left','marker-offset','max-height','max-width','min-height',
'min-width','orphans','outline','outline-color','outline-style','outline-width','overflow','padding',
'padding-top','padding-right','padding-bottom','padding-left','quotes','right','size','text-indent',
'top','width','word-spacing','z-index','opacity','outline-offset'];*/


CSSStyleSubject.cssProperties = ['azimuth','background','background-attachment','background-color','background-image','background-position','background-repeat','border-collapse','border-color','border-spacing','border-style','border-top','border-top-color','border-right-color','border-bottom-color','border-left-color','border-top-style','border-right-style','border-bottom-style','border-left-style','border-top-width','border-right-width','border-bottom-width','border-left-width','border-width','bottom','clear','clip','color','content','cursor','direction','display','elevation','empty-cells','css-float','font','font-family','font-size','font-size-adjust','font-stretch','font-style','font-variant','font-weight','height','left','letter-spacing','line-height','list-style','list-style-image','list-style-position','list-style-type','margin','margin-top','margin-right','margin-bottom','margin-left','max-height','max-width','min-height','min-width','orphans','outline','outline-color','outline-style','outline-width','overflow','padding','padding-top','padding-right','padding-bottom','padding-left','pause','position','right','size','table-layout','text-align','text-decoration','text-indent','text-shadow','text-transform','top','vertical-align','visibility','white-space','width','word-spacing','z-index','opacity','outline-offset','overflow-x','overflow-y'];


// chains several Animator objects together
function AnimatorChain(animators, options) {
	this.animators = animators;
	this.setOptions(options);
	for (var i=0; i<this.animators.length; i++) {
		this.listenTo(this.animators[i]);
	}
	this.forwards = false;
	this.current = 0;
}

AnimatorChain.prototype = {
	// apply defaults
	setOptions: function(options) {
		this.options = Animator.applyDefaults({
			// by default, each call to AnimatorChain.play() calls jumpTo(0) of each animator
			// before playing, which can cause flickering if you have multiple animators all
			// targeting the same element. Set this to false to avoid this.
			resetOnPlay: true
		}, options);
	},
	// play each animator in turn
	play: function() {
		this.forwards = true;
		this.current = -1;
		if (this.options.resetOnPlay) {
			for (var i=0; i<this.animators.length; i++) {
				this.animators[i].jumpTo(0);
			}
		}
		this.advance();
	},
	// play all animators backwards
	reverse: function() {
		this.forwards = false;
		this.current = this.animators.length;
		if (this.options.resetOnPlay) {
			for (var i=0; i<this.animators.length; i++) {
				this.animators[i].jumpTo(1);
			}
		}
		this.advance();
	},
	// if we have just play()'d, then call reverse(), and vice versa
	toggle: function() {
		if (this.forwards) {
			this.seekTo(0);
		} else {
			this.seekTo(1);
		}
	},
	// internal: install an event listener on an animator's onComplete option
	// to trigger the next animator
	listenTo: function(animator) {
		var oldOnComplete = animator.options.onComplete;
		var _this = this;
		animator.options.onComplete = function() {
			if (oldOnComplete) oldOnComplete.call(animator);
			_this.advance();
		}
	},
	// play the next animator
	advance: function() {
		if (this.forwards) {
			if (this.animators[this.current + 1] == null) return;
			this.current++;
			this.animators[this.current].play();
		} else {
			if (this.animators[this.current - 1] == null) return;
			this.current--;
			this.animators[this.current].reverse();
		}
	},
	// this function is provided for drop-in compatibility with Animator objects,
	// but only accepts 0 and 1 as target values
	seekTo: function(target) {
		if (target <= 0) {
			this.forwards = false;
			this.animators[this.current].seekTo(0);
		} else {
			this.forwards = true;
			this.animators[this.current].seekTo(1);
		}
	}
}

// an Accordion is a class that creates and controls a number of Animators. An array of elements is passed in,
// and for each element an Animator and a activator button is created. When an Animator's activator button is
// clicked, the Animator and all before it seek to 0, and all Animators after it seek to 1. This can be used to
// create the classic Accordion effect, hence the name.
// see setOptions for arguments
function Accordion(options) {
	this.setOptions(options);
	var selected = this.options.initialSection, current;
	if (this.options.rememberance) {
		current = document.location.hash.substring(1);
	}
	this.rememberanceTexts = [];
	this.ans = [];
	var _this = this;
	for (var i=0; i<this.options.sections.length; i++) {
		var el = this.options.sections[i];
		var an = new Animator(this.options.animatorOptions);
		var from = this.options.from + (this.options.shift * i);
		var to = this.options.to + (this.options.shift * i);
		an.addSubject(new NumericalStyleSubject(el, this.options.property, from, to, this.options.units));
		an.jumpTo(0);
		var activator = this.options.getActivator(el);
		activator.index = i;
		activator.onclick = function(){_this.show(this.index)};
		this.ans[this.ans.length] = an;
		this.rememberanceTexts[i] = activator.innerHTML.replace(/\s/g, "");
		if (this.rememberanceTexts[i] === current) {
			selected = i;
		}
	}
	this.show(selected);
}

Accordion.prototype = {
	// apply defaults
	setOptions: function(options) {
		this.options = Object.extend({
			// REQUIRED: an array of elements to use as the accordion sections
			sections: null,
			// a function that locates an activator button element given a section element.
			// by default it takes a button id from the section's "activator" attibute
			getActivator: function(el) {return document.getElementById(el.getAttribute("activator"))},
			// shifts each animator's range, for example with options {from:0,to:100,shift:20}
			// the animators' ranges will be 0-100, 20-120, 40-140 etc.
			shift: 0,
			// the first page to show
			initialSection: 0,
			// if set to true, document.location.hash will be used to preserve the open section across page reloads 
			rememberance: true,
			// constructor arguments to the Animator objects
			animatorOptions: {}
		}, options || {});
	},
	show: function(section) {
		for (var i=0; i<this.ans.length; i++) {
			this.ans[i].seekTo(i > section ? 1 : 0);
		}
		if (this.options.rememberance) {
			document.location.hash = this.rememberanceTexts[section];
		}
	}
}

/**
 *
 * SoundManager 2 Demo: 360-degree / "donut player"
 * ------------------------------------------------
 * http://schillmania.com/projects/soundmanager2/
 *
 * An inline player with a circular UI.
 * Based on the original SM2 inline player.
 * Inspired by Apple's preview feature in the
 * iTunes music store (iPhone), among others.
 *
 * Requires SoundManager 2 Javascript API.
 * Also uses Bernie's Better Animation Class (BSD):
 * http://www.berniecode.com/writing/animator.html
 *
*/

/*jslint white: false, onevar: true, undef: true, nomen: false, eqeqeq: true, plusplus: false, bitwise: true, regexp: false, newcap: true, immed: true */
/*global document, window, soundManager, navigator */

var threeSixtyPlayer, // instance
    ThreeSixtyPlayer; // constructor

(function(window) {

function ThreeSixtyPlayer() {

  var self = this,
      pl = this,
      sm = soundManager, // soundManager instance
      uA = navigator.userAgent,
      isIE = (uA.match(/msie/i)),
      isOpera = (uA.match(/opera/i)),
      isSafari = (uA.match(/safari/i)),
      isChrome = (uA.match(/chrome/i)),
      isFirefox = (uA.match(/firefox/i)),
      isTouchDevice = (uA.match(/ipad|iphone/i)),
      hasRealCanvas = (typeof window.G_vmlCanvasManager === 'undefined' && typeof document.createElement('canvas').getContext('2d') !== 'undefined'),
      // I dunno what Opera doesn't like about this. I'm probably doing it wrong.
      fullCircle = (isOpera?359.9:360);

  // CSS class for ignoring MP3 links
  this.excludeClass = 'threesixty-exclude';
  this.links = [];
  this.sounds = [];
  this.soundsByURL = [];
  this.indexByURL = [];
  this.lastSound = null;
  this.lastTouchedSound = null;
  this.soundCount = 0;
  this.oUITemplate = null;
  this.oUIImageMap = null;
  this.vuMeter = null;
  this.callbackCount = 0;
  this.peakDataHistory = [];
  this.firstBuffering = true;
  this.firstPlayTime = null;
  this.bufferDelay = 0;

  // 360player configuration options
  this.config = {

    playNext: false,   // stop after one sound, or play through list until end
    autoPlay: false,   // start playing the first sound right away
    allowMultiple: false,  // let many sounds play at once (false = only one sound playing at a time)
    loadRingColor: '#d5d5d5', // how much has loaded
    playRingColor: '#d5d5d5', // how much has played
    backgroundRingColor: '#d5d5d5', // color shown underneath load + play ("not yet loaded" color)

    // optional segment/annotation (metadata) stuff..
    segmentRingColor: '#d5d5d5', // metadata/annotation (segment) colors
    segmentRingColorAlt: '#d5d5d5',
    loadRingColorMetadata: '#d5d5d5', // "annotations" load color
    playRingColorMetadata: '#d5d5d5', // how much has played when metadata is present

    circleDiameter: 256, // set dynamically according to values from CSS
    circleRadius: 128,
    animDuration: 500,
    animTransition: window.Animator.tx.bouncy, // http://www.berniecode.com/writing/animator.html
    showHMSTime: false, // hours:minutes:seconds vs. seconds-only
    scaleFont: true,  // also set the font size (if possible) while animating the circle

    // optional: spectrum or EQ graph in canvas (not supported in IE <9, too slow via ExCanvas)
    useWaveformData: false,
    waveformDataColor: '#d5d5d5',
    waveformDataDownsample: 3, // use only one in X (of a set of 256 values) - 1 means all 256
    waveformDataOutside: false,
    waveformDataConstrain: false, // if true, +ve values only - keep within inside circle
    waveformDataLineRatio: 1.44,

    // "spectrum frequency" option
    useEQData: true,
    eqDataColor: '#d5d5d5',
    eqDataDownsample: 1, // use only one in X (of 256 values)
    eqDataOutside: true,
    eqDataLineRatio: 1,

    // enable "amplifier" (canvas pulses like a speaker) effect
    usePeakData: true,
    peakDataColor: '#d5d5d5',
    peakDataOutside: true,
    peakDataLineRatio: 0.5,

    useAmplifier: true, // "pulse" like a speaker

    fontSizeMax: null, // set according to CSS

    scaleArcWidth: 1.6,  // thickness factor of playback progress ring

    useFavIcon: false // Experimental (also requires usePeakData: true).. Try to draw a "VU Meter" in the favicon area, if browser supports it (Firefox + Opera as of 2009)

  };

  this.css = {

    // CSS class names appended to link during various states
    sDefault: 'sm2_link', // default state
    sBuffering: 'sm2_buffering',
    sPlaying: 'sm2_playing',
    sPaused: 'sm2_paused'

  };

  this.addEventHandler = (typeof window.addEventListener !== 'undefined' ? function(o, evtName, evtHandler) {
    return o.addEventListener(evtName,evtHandler,false);
  } : function(o, evtName, evtHandler) {
    o.attachEvent('on'+evtName,evtHandler);
  });

  this.removeEventHandler = (typeof window.removeEventListener !== 'undefined' ? function(o, evtName, evtHandler) {
    return o.removeEventListener(evtName,evtHandler,false);
  } : function(o, evtName, evtHandler) {
    return o.detachEvent('on'+evtName,evtHandler);
  });

  this.hasClass = function(o,cStr) {
    return typeof(o.className)!=='undefined'?o.className.match(new RegExp('(\\s|^)'+cStr+'(\\s|$)')):false;
  };

  this.addClass = function(o,cStr) {

    if (!o || !cStr || self.hasClass(o,cStr)) {
      return false;
    }
    o.className = (o.className?o.className+' ':'')+cStr;

  };

  this.removeClass = function(o,cStr) {

    if (!o || !cStr || !self.hasClass(o,cStr)) {
      return false;
    }
    o.className = o.className.replace(new RegExp('( '+cStr+')|('+cStr+')','g'),'');

  };

  this.getElementsByClassName = function(className,tagNames,oParent) {

    var doc = (oParent||document),
        matches = [], i,j, nodes = [];
    if (typeof tagNames !== 'undefined' && typeof tagNames !== 'string') {
      for (i=tagNames.length; i--;) {
        if (!nodes || !nodes[tagNames[i]]) {
          nodes[tagNames[i]] = doc.getElementsByTagName(tagNames[i]);
        }
      }
    } else if (tagNames) {
      nodes = doc.getElementsByTagName(tagNames);
    } else {
      nodes = doc.all||doc.getElementsByTagName('*');
    }
    if (typeof(tagNames)!=='string') {
      for (i=tagNames.length; i--;) {
        for (j=nodes[tagNames[i]].length; j--;) {
          if (self.hasClass(nodes[tagNames[i]][j],className)) {
            matches.push(nodes[tagNames[i]][j]);
          }
        }
      }
    } else {
      for (i=0; i<nodes.length; i++) {
        if (self.hasClass(nodes[i],className)) {
          matches.push(nodes[i]);
        }
      }
    }
    return matches;

  };

  this.getParentByNodeName = function(oChild,sParentNodeName) {

    if (!oChild || !sParentNodeName) {
      return false;
    }
    sParentNodeName = sParentNodeName.toLowerCase();
    while (oChild.parentNode && sParentNodeName !== oChild.parentNode.nodeName.toLowerCase()) {
      oChild = oChild.parentNode;
    }
    return (oChild.parentNode && sParentNodeName === oChild.parentNode.nodeName.toLowerCase()?oChild.parentNode:null);

  };

  this.getParentByClassName = function(oChild,sParentClassName) {

    if (!oChild || !sParentClassName) {
      return false;
    }
    while (oChild.parentNode && !self.hasClass(oChild.parentNode,sParentClassName)) {
      oChild = oChild.parentNode;
    }
    return (oChild.parentNode && self.hasClass(oChild.parentNode,sParentClassName)?oChild.parentNode:null);

  };

  this.getSoundByURL = function(sURL) {
    return (typeof self.soundsByURL[sURL] !== 'undefined'?self.soundsByURL[sURL]:null);
  };

  this.isChildOfNode = function(o,sNodeName) {

    if (!o || !o.parentNode) {
      return false;
    }
    sNodeName = sNodeName.toLowerCase();
    do {
      o = o.parentNode;
    } while (o && o.parentNode && o.nodeName.toLowerCase() !== sNodeName);
    return (o && o.nodeName.toLowerCase() === sNodeName?o:null);

  };

  this.isChildOfClass = function(oChild,oClass) {

    if (!oChild || !oClass) {
      return false;
    }
    while (oChild.parentNode && !self.hasClass(oChild,oClass)) {
      oChild = self.findParent(oChild);
    }
    return (self.hasClass(oChild,oClass));

  };

  this.findParent = function(o) {

    if (!o || !o.parentNode) {
      return false;
    }
    o = o.parentNode;
    if (o.nodeType === 2) {
      while (o && o.parentNode && o.parentNode.nodeType === 2) {
        o = o.parentNode;
      }
    }
    return o;

  };

  this.getStyle = function(o,sProp) {

    // http://www.quirksmode.org/dom/getstyles.html
    try {
      if (o.currentStyle) {
        return o.currentStyle[sProp];
      } else if (window.getComputedStyle) {
        return document.defaultView.getComputedStyle(o,null).getPropertyValue(sProp);
      }
    } catch(e) {
      // oh well
    }
    return null;

  };

  this.findXY = function(obj) {

    var curleft = 0, curtop = 0;
    do {
      curleft += obj.offsetLeft;
      curtop += obj.offsetTop;
    } while (!!(obj = obj.offsetParent));
    return [curleft,curtop];

  };

  this.getMouseXY = function(e) {

    // http://www.quirksmode.org/js/events_properties.html
    e = e?e:window.event;
    if (isTouchDevice && e.touches) {
      e = e.touches[0];
    }
    if (e.pageX || e.pageY) {
      return [e.pageX,e.pageY];
    } else if (e.clientX || e.clientY) {
      return [e.clientX+self.getScrollLeft(),e.clientY+self.getScrollTop()];
    }

  };

  this.getScrollLeft = function() {
    return (document.body.scrollLeft+document.documentElement.scrollLeft);
  };

  this.getScrollTop = function() {
    return (document.body.scrollTop+document.documentElement.scrollTop);
  };

  this.events = {

    // handlers for sound events as they're started/stopped/played

    play: function() {
      if (self.firstBuffering) {
        self.firstPlayTime = +new Date();
      }
      pl.removeClass(this._360data.oUIBox,this._360data.className);
      this._360data.className = pl.css.sPlaying;
      pl.addClass(this._360data.oUIBox,this._360data.className);
      self.fanOut(this);
    },

    stop: function() {
      pl.removeClass(this._360data.oUIBox,this._360data.className);
      this._360data.className = '';
      self.fanIn(this);
    },

    pause: function() {
      pl.removeClass(this._360data.oUIBox,this._360data.className);
      this._360data.className = pl.css.sPaused;
      pl.addClass(this._360data.oUIBox,this._360data.className);
    },

    resume: function() {
      pl.removeClass(this._360data.oUIBox,this._360data.className);
      this._360data.className = pl.css.sPlaying;
      pl.addClass(this._360data.oUIBox,this._360data.className);      
    },

    finish: function() {
      var nextLink;
      pl.removeClass(this._360data.oUIBox,this._360data.className);
      this._360data.className = '';
      // self.clearCanvas(this._360data.oCanvas);
      this._360data.didFinish = true; // so fan draws full circle
      self.fanIn(this);
      if (pl.config.playNext) {
        nextLink = (pl.indexByURL[this._360data.oLink.href]+1);
        if (nextLink<pl.links.length) {
          pl.handleClick({'target':pl.links[nextLink]});
        }
      }
    },

    whileloading: function() {
      if (this.paused) {
        self.updatePlaying.apply(this);
      }
    },

    whileplaying: function() {
      self.updatePlaying.apply(this);
      this._360data.fps++;
    },

    bufferchange: function() {
      if (this.isBuffering) {
        pl.addClass(this._360data.oUIBox,pl.css.sBuffering);
      } else {
        self.events.donebuffering();
        pl.removeClass(this._360data.oUIBox,pl.css.sBuffering);
      }
    },

    donebuffering: function() {
      if (self.firstBuffering) {
        self.events.donefirstbuffering();
        self.firstBuffering = false;
      }
    },

    donefirstbuffering: function() {
      self.bufferDelay = (+new Date() - self.firstPlayTime);
    }
  };

  this.stopEvent = function(e) {

   if (typeof e !== 'undefined' && typeof e.preventDefault !== 'undefined') {
      e.preventDefault();
    } else if (typeof window.event !== 'undefined' && typeof window.event.returnValue !== 'undefined') {
      window.event.returnValue = false;
    }
    return false;

  };

  this.getTheDamnLink = (isIE)?function(e) {
    // I really didn't want to have to do this.
    return (e && e.target?e.target:window.event.srcElement);
  }:function(e) {
    return e.target;
  };

  this.handleClick = function(e) {

    // a sound link was clicked
    if (e.button > 1) {
      // only catch left-clicks
      return true;
    }

    var o = self.getTheDamnLink(e),
        sURL, soundURL, thisSound, oContainer, has_vis, diameter;

    if (o.nodeName.toLowerCase() !== 'a') {
      o = self.isChildOfNode(o,'a');
      if (!o) {
        return true;
      }
    }

    if (!self.isChildOfClass(o,'ui360')) {
      // not a link we're interested in
      return true;
    }

    sURL = o.getAttribute('href');

    if (!o.href || !sm.canPlayLink(o) || self.hasClass(o,self.excludeClass)) {
      return true; // pass-thru for non-MP3/non-links
    }

    sm._writeDebug('handleClick()');
    soundURL = (o.href);
    thisSound = self.getSoundByURL(soundURL);

    if (thisSound) {

      // already exists
      if (thisSound === self.lastSound) {
        // and was playing (or paused)
        thisSound.togglePause();
      } else {
        // different sound
        thisSound.togglePause(); // start playing current
        sm._writeDebug('sound different than last sound: '+self.lastSound.id);
        if (!self.config.allowMultiple && self.lastSound) {
          self.stopSound(self.lastSound);
        }
      }

    } else {

      // append some dom shiz, make noise

      oContainer = o.parentNode;
      has_vis = (self.getElementsByClassName('ui360-vis','div',oContainer.parentNode).length);

      // create sound
      thisSound = sm.createSound({
       id:'ui360Sound'+(self.soundCount++),
       url:soundURL,
       onplay:self.events.play,
       onstop:self.events.stop,
       onpause:self.events.pause,
       onresume:self.events.resume,
       onfinish:self.events.finish,
       onbufferchange:self.events.bufferchange,
       whileloading:self.events.whileloading,
       whileplaying:self.events.whileplaying,
       useWaveformData:(has_vis && self.config.useWaveformData),
       useEQData:(has_vis && self.config.useEQData),
       usePeakData:(has_vis && self.config.usePeakData)
      });

      // tack on some custom data

      diameter = parseInt(self.getElementsByClassName('sm2-360ui','div',oContainer)[0].offsetWidth, 10);

      thisSound._360data = {
        oUI360: self.getParentByClassName(o,'ui360'), // the (whole) entire container
        oLink: o, // DOM node for reference within SM2 object event handlers
        className: self.css.sPlaying,
        oUIBox: self.getElementsByClassName('sm2-360ui','div',oContainer)[0],
        oCanvas: self.getElementsByClassName('sm2-canvas','canvas',oContainer)[0],
        oButton: self.getElementsByClassName('sm2-360btn','span',oContainer)[0],
        oTiming: self.getElementsByClassName('sm2-timing','div',oContainer)[0],
        oCover: self.getElementsByClassName('sm2-cover','div',oContainer)[0],
        circleDiameter: diameter,
        circleRadius: diameter/2,
        lastTime: null,
        didFinish: null,
        pauseCount:0,
        radius:0,
        fontSize: 1,
        fontSizeMax: self.config.fontSizeMax,
        scaleFont: (has_vis && self.config.scaleFont),
        showHMSTime: has_vis,
        amplifier: (has_vis && self.config.usePeakData?0.9:1), // TODO: x1 if not being used, else use dynamic "how much to amplify by" value
        radiusMax: diameter*0.175, // circle radius
        width:0,
        widthMax: diameter*0.4, // width of the outer ring
        lastValues: {
          bytesLoaded: 0,
          bytesTotal: 0,
          position: 0,
          durationEstimate: 0
        }, // used to track "last good known" values before sound finish/reset for anim
        animating: false,
        oAnim: new window.Animator({
          duration: self.config.animDuration,
          transition:self.config.animTransition,
          onComplete: function() {
            // var thisSound = this;
            // thisSound._360data.didFinish = false; // reset full circle
          }
        }),
        oAnimProgress: function(nProgress) {
          var thisSound = this;
          thisSound._360data.radius = parseInt(thisSound._360data.radiusMax*thisSound._360data.amplifier*nProgress, 10);
          thisSound._360data.width = parseInt(thisSound._360data.widthMax*thisSound._360data.amplifier*nProgress, 10);
          if (thisSound._360data.scaleFont && thisSound._360data.fontSizeMax !== null) {
            thisSound._360data.oTiming.style.fontSize = parseInt(Math.max(1,thisSound._360data.fontSizeMax*nProgress), 10)+'px';
            thisSound._360data.oTiming.style.opacity = nProgress;
          }
          if (thisSound.paused || thisSound.playState === 0 || thisSound._360data.lastValues.bytesLoaded === 0 || thisSound._360data.lastValues.position === 0) {
            self.updatePlaying.apply(thisSound);
          }
        },
        fps: 0
      };

      // "Metadata" (annotations)
      if (typeof self.Metadata !== 'undefined' && self.getElementsByClassName('metadata','div',thisSound._360data.oUI360).length) {
        thisSound._360data.metadata = new self.Metadata(thisSound,self);
      }

      // minimize ze font
      if (thisSound._360data.scaleFont && thisSound._360data.fontSizeMax !== null) {
        thisSound._360data.oTiming.style.fontSize = '1px';
      }

      // set up ze animation
      thisSound._360data.oAnim.addSubject(thisSound._360data.oAnimProgress,thisSound);

      // animate the radius out nice
      self.refreshCoords(thisSound);

      self.updatePlaying.apply(thisSound);

      self.soundsByURL[soundURL] = thisSound;
      self.sounds.push(thisSound);
      if (!self.config.allowMultiple && self.lastSound) {
        self.stopSound(self.lastSound);
      }
      thisSound.play();

    }

    self.lastSound = thisSound; // reference for next call

    if (typeof e !== 'undefined' && typeof e.preventDefault !== 'undefined') {
      e.preventDefault();
    } else if (typeof window.event !== 'undefined') {
      window.event.returnValue = false;
    }
    return false;

  };

  this.fanOut = function(oSound) {

     var thisSound = oSound;
     if (thisSound._360data.animating === 1) {
       return false;
     }
     thisSound._360data.animating = 0;
     soundManager._writeDebug('fanOut: '+thisSound.id+': '+thisSound._360data.oLink.href);
     thisSound._360data.oAnim.seekTo(1); // play to end
     window.setTimeout(function() {
       // oncomplete hack
       thisSound._360data.animating = 0;
     },self.config.animDuration+20);

  };

  this.fanIn = function(oSound) {

     var thisSound = oSound;
     if (thisSound._360data.animating === -1) {
       return false;
     }
     thisSound._360data.animating = -1;
     soundManager._writeDebug('fanIn: '+thisSound.id+': '+thisSound._360data.oLink.href);
     // massive hack
     thisSound._360data.oAnim.seekTo(0); // play to end
     window.setTimeout(function() {
       // reset full 360 fill after animation has completed (oncomplete hack)
       thisSound._360data.didFinish = false;
       thisSound._360data.animating = 0;
       self.resetLastValues(thisSound);
     }, self.config.animDuration+20);

  };

  this.resetLastValues = function(oSound) {
    oSound._360data.lastValues.position = 0;
  };

  this.refreshCoords = function(thisSound) {

    thisSound._360data.canvasXY = self.findXY(thisSound._360data.oCanvas);
    thisSound._360data.canvasMid = [thisSound._360data.circleRadius,thisSound._360data.circleRadius];
    thisSound._360data.canvasMidXY = [thisSound._360data.canvasXY[0]+thisSound._360data.canvasMid[0], thisSound._360data.canvasXY[1]+thisSound._360data.canvasMid[1]];

  };

  this.stopSound = function(oSound) {

    soundManager._writeDebug('stopSound: '+oSound.id);
    soundManager.stop(oSound.id);
    if (!isTouchDevice) { // iOS 4.2+ security blocks onfinish() -> playNext() if we set a .src in-between(?)
      soundManager.unload(oSound.id);
    }

  };

  this.buttonClick = function(e) {

    var o = e?(e.target?e.target:e.srcElement):window.event.srcElement;
    self.handleClick({target:self.getParentByClassName(o,'sm2-360ui').nextSibling}); // link next to the nodes we inserted
    return false;

  };

  this.drawSolidArc = function(oCanvas, color, radius, width, radians, startAngle, noClear) {

    // thank you, http://www.snipersystems.co.nz/community/polarclock/tutorial.html

    var x = radius,
        y = radius,
        canvas = oCanvas,
        ctx, innerRadius, doesntLikeZero, endPoint;

    if (canvas.getContext){
      // use getContext to use the canvas for drawing
      ctx = canvas.getContext('2d');
    }

    // re-assign canvas as the actual context
    oCanvas = ctx;

    if (!noClear) {
      self.clearCanvas(canvas);
    }
    // ctx.restore();

    if (color) {
      ctx.fillStyle = color;
    }

    oCanvas.beginPath();

    if (isNaN(radians)) {
      radians = 0;
    }

    innerRadius = radius-width;
    doesntLikeZero = (isOpera || isSafari); // safari 4 doesn't actually seem to mind.

    if (!doesntLikeZero || (doesntLikeZero && radius > 0)) {
      oCanvas.arc(0, 0, radius, startAngle, radians, false);
      endPoint = self.getArcEndpointCoords(innerRadius, radians);
      oCanvas.lineTo(endPoint.x, endPoint.y);
      oCanvas.arc(0, 0, innerRadius, radians, startAngle, true);
      oCanvas.closePath();
      oCanvas.fill();
    }

  };

  this.getArcEndpointCoords = function(radius, radians) {

    return {
      x: radius * Math.cos(radians), 
      y: radius * Math.sin(radians)
    };

  };

  this.deg2rad = function(nDeg) {
    return (nDeg * Math.PI/180);
  };

  this.rad2deg = function(nRad) {
    return (nRad * 180/Math.PI);
  };

  this.getTime = function(nMSec,bAsString) {

    // convert milliseconds to mm:ss, return as object literal or string
    var nSec = Math.floor(nMSec/1000),
        min = Math.floor(nSec/60),
        sec = nSec-(min*60);
    // if (min === 0 && sec === 0) return null; // return 0:00 as null
    return (bAsString?(min+':'+(sec<10?'0'+sec:sec)):{'min':min,'sec':sec});

  };

  this.clearCanvas = function(oCanvas) {

    var canvas = oCanvas,
        ctx = null,
        width, height;
    if (canvas.getContext){
      // use getContext to use the canvas for drawing
      ctx = canvas.getContext('2d');
    }
    width = canvas.offsetWidth;
    height = canvas.offsetHeight;
    ctx.clearRect(-(width/2), -(height/2), width, height);

  };

  this.updatePlaying = function() {

    var timeNow = (this._360data.showHMSTime?self.getTime(this.position,true):parseInt(this.position/1000, 10));
    var ringScaleFactor = self.config.scaleArcWidth;

    if (this.bytesLoaded) {
      this._360data.lastValues.bytesLoaded = this.bytesLoaded;
      this._360data.lastValues.bytesTotal = this.bytesTotal;
    }

    if (this.position) {
      this._360data.lastValues.position = this.position;
    }

    if (this.durationEstimate) {
      this._360data.lastValues.durationEstimate = this.durationEstimate;
    }

    // background ring
    self.drawSolidArc(this._360data.oCanvas,self.config.backgroundRingColor,this._360data.width,this._360data.radius * ringScaleFactor,self.deg2rad(fullCircle),false);

    /*
    // loaded ring
    self.drawSolidArc(this._360data.oCanvas,(this._360data.metadata?self.config.loadRingColorMetadata:self.config.loadRingColor),this._360data.width,this._360data.radius * ringScaleFactor,self.deg2rad(fullCircle*(this._360data.lastValues.bytesLoaded/this._360data.lastValues.bytesTotal)),0,true);

    // don't draw if 0 (full black circle in Opera)
    if (this._360data.lastValues.position !== 0) {
      self.drawSolidArc(this._360data.oCanvas,(this._360data.metadata?self.config.playRingColorMetadata:self.config.playRingColor),this._360data.width,this._360data.radius * ringScaleFactor,self.deg2rad((this._360data.didFinish===1?fullCircle:fullCircle*(this._360data.lastValues.position/this._360data.lastValues.durationEstimate))),0,true);
    }*/

    // metadata goes here
    if (this._360data.metadata) {
      this._360data.metadata.events.whileplaying();
    }

    if (timeNow !== this._360data.lastTime) {
      this._360data.lastTime = timeNow;
      this._360data.oTiming.innerHTML = timeNow;
    }

    // draw spectrum, if applicable
    if ((this.instanceOptions.useWaveformData || this.instanceOptions.useEQData) && hasRealCanvas) { // IE <9 can render maybe 3 or 4 FPS when including the wave/EQ, so don't bother.
      self.updateWaveform(this);
    }

    if (self.config.useFavIcon && self.vuMeter) {
      self.vuMeter.updateVU(this);
    }

  };

  this.updateWaveform = function(oSound) {

    if ((!self.config.useWaveformData && !self.config.useEQData) || (!sm.features.waveformData && !sm.features.eqData)) {
      // feature not enabled..
      return false;
    }

    if (!oSound.waveformData.left.length && !oSound.eqData.length && !oSound.peakData.left) {
      // no data (or errored out/paused/unavailable?)
      return false;
    }

    /* use for testing the data */
    /*
     for (i=0; i<256; i++) {
       oSound.eqData[i] = 1-(i/256);
     }
    */

    var oCanvas = oSound._360data.oCanvas.getContext('2d'),
        offX = 0,
        offY = parseInt(oSound._360data.circleDiameter/2, 10),
        scale = offY/2, // Y axis (+/- this distance from 0)
        // lineWidth = Math.floor(oSound._360data.circleDiameter-(oSound._360data.circleDiameter*0.175)/(oSound._360data.circleDiameter/255)); // width for each line
        lineWidth = 1,
        lineHeight = 1,
        thisY = 0,
        offset = offY,
        i, j, direction, downSample, dataLength, sampleCount, startAngle, endAngle, waveData, innerRadius, perItemAngle, yDiff, eqSamples, playedAngle, iAvg, nPeak;

    if (self.config.useWaveformData) {
      // raw waveform
      downSample = self.config.waveformDataDownsample; // only sample X in 256 (greater number = less sample points)
      downSample = Math.max(1,downSample); // make sure it's at least 1
      dataLength = 256;
      sampleCount = (dataLength/downSample);
      startAngle = 0;
      endAngle = 0;
      waveData = null;
      innerRadius = (self.config.waveformDataOutside?1:(self.config.waveformDataConstrain?0.5:0.565));
      scale = (self.config.waveformDataOutside?0.7:0.75);
      perItemAngle = self.deg2rad((360/sampleCount)*self.config.waveformDataLineRatio); // 0.85 = clean pixel lines at 150? // self.deg2rad(360*(Math.max(1,downSample-1))/sampleCount);
      for (i=0; i<dataLength; i+=downSample) {
        startAngle = self.deg2rad(360*(i/(sampleCount)*1/downSample)); // +0.67 - counter for spacing
        endAngle = startAngle+perItemAngle;
        waveData = oSound.waveformData.left[i];
        if (waveData<0 && self.config.waveformDataConstrain) {
          waveData = Math.abs(waveData);
        }
        self.drawSolidArc(oSound._360data.oCanvas,self.config.waveformDataColor,oSound._360data.width*innerRadius*(2-self.config.scaleArcWidth),oSound._360data.radius*scale*1.25*waveData,endAngle,startAngle,true);
      }
    }

    if (self.config.useEQData) {
      // EQ spectrum
      downSample = self.config.eqDataDownsample; // only sample N in 256
      yDiff = 0;
      downSample = Math.max(1,downSample); // make sure it's at least 1
      eqSamples = 192; // drop the last 25% of the spectrum (>16500 Hz), most stuff won't actually use it.
      sampleCount = (eqSamples/downSample);
      innerRadius = (self.config.eqDataOutside?1:0.565);
      direction = (self.config.eqDataOutside?-1:1);
      scale = (self.config.eqDataOutside?0.5:0.75);
      startAngle = 0;
      endAngle = 0;
      perItemAngle = self.deg2rad((360/sampleCount)*self.config.eqDataLineRatio); // self.deg2rad(360/(sampleCount+1));
      playedAngle = self.deg2rad((oSound._360data.didFinish===1?360:360*(oSound._360data.lastValues.position/oSound._360data.lastValues.durationEstimate)));
      j=0;
      iAvg = 0;
      for (i=0; i<eqSamples; i+=downSample) {
        startAngle = self.deg2rad(360*(i/eqSamples));
        endAngle = startAngle+perItemAngle;
        self.drawSolidArc(oSound._360data.oCanvas,self.config.playRingColor,oSound._360data.width*innerRadius,oSound._360data.radius*scale*(oSound.eqData.left[i]*direction),endAngle,startAngle,true);
      }
    }

    if (self.config.usePeakData) {
      if (!oSound._360data.animating) {
        nPeak = (oSound.peakData.left||oSound.peakData.right);
        // GIANT HACK: use EQ spectrum data for bass frequencies
        eqSamples = 3;
        for (i=0; i<eqSamples; i++) {
          nPeak = (nPeak||oSound.eqData[i]);
        }
        oSound._360data.amplifier = (self.config.useAmplifier?(0.9+(nPeak*0.1)):1);
        oSound._360data.radiusMax = oSound._360data.circleDiameter*0.175*oSound._360data.amplifier;
        oSound._360data.widthMax = oSound._360data.circleDiameter*0.4*oSound._360data.amplifier;
        oSound._360data.radius = parseInt(oSound._360data.radiusMax*oSound._360data.amplifier, 10);
        oSound._360data.width = parseInt(oSound._360data.widthMax*oSound._360data.amplifier, 10);
      }
    }

  };

  this.getUIHTML = function(diameter) {

    return [
     '<canvas class="sm2-canvas" width="'+diameter+'" height="'+diameter+'"></canvas>',
     ' <span class="sm2-360btn sm2-360btn-default"></span>', // note use of imageMap, edit or remove if you use a different-size image.
     ' <div class="sm2-timing'+(navigator.userAgent.match(/safari/i)?' alignTweak':'')+'"></div>', // + Ever-so-slight Safari horizontal alignment tweak
     ' <div class="sm2-cover"></div>'
    ];

  };

  this.uiTest = function(sClass) {

    // fake a 360 UI so we can get some numbers from CSS, etc.

    var oTemplate = document.createElement('div'),
        oFakeUI, oFakeUIBox, oTemp, fakeDiameter, uiHTML, circleDiameter, circleRadius, fontSizeMax, oTiming;

    oTemplate.className = 'sm2-360ui';

    oFakeUI = document.createElement('div');
    oFakeUI.className = 'ui360'+(sClass?' '+sClass:''); // ui360 ui360-vis

    oFakeUIBox = oFakeUI.appendChild(oTemplate.cloneNode(true));

    oFakeUI.style.position = 'absolute';
    oFakeUI.style.left = '-9999px';

    oTemp = document.body.appendChild(oFakeUI);

    fakeDiameter = oFakeUIBox.offsetWidth;

    uiHTML = self.getUIHTML(fakeDiameter);

    oFakeUIBox.innerHTML = uiHTML[1]+uiHTML[2]+uiHTML[3];

    circleDiameter = parseInt(oFakeUIBox.offsetWidth, 10);
    circleRadius = parseInt(circleDiameter/2, 10);

    oTiming = self.getElementsByClassName('sm2-timing','div',oTemp)[0];
    fontSizeMax = parseInt(self.getStyle(oTiming,'font-size'), 10);
    if (isNaN(fontSizeMax)) {
      // getStyle() etc. didn't work.
      fontSizeMax = null;
    }

    // soundManager._writeDebug('diameter, font size: '+circleDiameter+','+fontSizeMax);

    oFakeUI.parentNode.removeChild(oFakeUI);

    uiHTML = oFakeUI = oFakeUIBox = oTemp = null;

    return {
      circleDiameter: circleDiameter,
      circleRadius: circleRadius,
      fontSizeMax: fontSizeMax
    };

  };

  this.init = function() {

    sm._writeDebug('threeSixtyPlayer.init()');

    var oItems = self.getElementsByClassName('ui360','div'),
        i, j, oLinks = [], is_vis = false, foundItems = 0, oCanvas, oCanvasCTX, oCover, diameter, radius, uiData, uiDataVis, oUI, oBtn, o, o2, oID;

    for (i=0,j=oItems.length; i<j; i++) {
      oLinks.push(oItems[i].getElementsByTagName('a')[0]);
      // remove "fake" play button (unsupported case)
      oItems[i].style.backgroundImage = 'none';
    }
    // grab all links, look for .mp3

    self.oUITemplate = document.createElement('div');
    self.oUITemplate.className = 'sm2-360ui';

    self.oUITemplateVis = document.createElement('div');
    self.oUITemplateVis.className = 'sm2-360ui';

    uiData = self.uiTest();

    self.config.circleDiameter = uiData.circleDiameter;
    self.config.circleRadius = uiData.circleRadius;
    // self.config.fontSizeMax = uiData.fontSizeMax;

    uiDataVis = self.uiTest('ui360-vis');

    self.config.fontSizeMax = uiDataVis.fontSizeMax;

    // canvas needs inline width and height, doesn't quite work otherwise
    self.oUITemplate.innerHTML = self.getUIHTML(self.config.circleDiameter).join('');

    self.oUITemplateVis.innerHTML = self.getUIHTML(uiDataVis.circleDiameter).join('');

    for (i=0,j=oLinks.length; i<j; i++) {
      if (sm.canPlayLink(oLinks[i]) && !self.hasClass(oLinks[i],self.excludeClass) && !self.hasClass(oLinks[i],self.css.sDefault)) {
        self.addClass(oLinks[i],self.css.sDefault); // add default CSS decoration
        self.links[foundItems] = (oLinks[i]);
        self.indexByURL[oLinks[i].href] = foundItems; // hack for indexing
        foundItems++;

        is_vis = self.hasClass(oLinks[i].parentNode, 'ui360-vis');

        diameter = (is_vis ? uiDataVis : uiData).circleDiameter;
        radius = (is_vis ? uiDataVis : uiData).circleRadius;

        // add canvas shiz
        oUI = oLinks[i].parentNode.insertBefore((is_vis?self.oUITemplateVis:self.oUITemplate).cloneNode(true),oLinks[i]);

        if (isIE && typeof window.G_vmlCanvasManager !== 'undefined') { // IE only
          o = oLinks[i].parentNode;
          o2 = document.createElement('canvas');
          o2.className = 'sm2-canvas';
          oID = 'sm2_canvas_'+parseInt(Math.random()*1048576, 10);
          o2.id = oID;
          o2.width = diameter;
          o2.height = diameter;
          oUI.appendChild(o2);
          window.G_vmlCanvasManager.initElement(o2); // Apply ExCanvas compatibility magic
          oCanvas = document.getElementById(oID);
        } else { 
          // add a handler for the button
          oCanvas = oLinks[i].parentNode.getElementsByTagName('canvas')[0];
        }
        oCover = self.getElementsByClassName('sm2-cover','div',oLinks[i].parentNode)[0];
        oBtn = oLinks[i].parentNode.getElementsByTagName('span')[0];
        self.addEventHandler(oBtn,'click',self.buttonClick);
        oCanvasCTX = oCanvas.getContext('2d');
        oCanvasCTX.translate(radius, radius);
        oCanvasCTX.rotate(self.deg2rad(-90)); // compensate for arc starting at EAST // http://stackoverflow.com/questions/319267/tutorial-for-html-canvass-arc-function
      }
    }
    if (foundItems>0) {
      self.addEventHandler(document,'click',self.handleClick);
      if (self.config.autoPlay) {
        self.handleClick({target:self.links[0],preventDefault:function(){}});
      }
    }
    sm._writeDebug('threeSixtyPlayer.init(): Found '+foundItems+' relevant items.');

    if (self.config.useFavIcon && typeof this.VUMeter !== 'undefined') {
      this.vuMeter = new this.VUMeter(this);
    }

  };

}

// Optional: VU Meter component

ThreeSixtyPlayer.prototype.VUMeter = function(oParent) {

  var self = oParent,
      me = this,
      _head = document.getElementsByTagName('head')[0],
      isOpera = (navigator.userAgent.match(/opera/i)),
      isFirefox = (navigator.userAgent.match(/firefox/i));

  this.vuMeterData = [];
  this.vuDataCanvas = null;

  this.setPageIcon = function(sDataURL) {

    if (!self.config.useFavIcon || !self.config.usePeakData || !sDataURL) {
      return false;
    }

    var link = document.getElementById('sm2-favicon');
    if (link) {
      _head.removeChild(link);
      link = null;
    }
    if (!link) {
      link = document.createElement('link');
      link.id = 'sm2-favicon';
      link.rel = 'shortcut icon';
      link.type = 'image/png';
      link.href = sDataURL;
      document.getElementsByTagName('head')[0].appendChild(link);
    }

  };

  this.resetPageIcon = function() {

    if (!self.config.useFavIcon) {
      return false;
    }
    var link = document.getElementById('favicon');
    if (link) {
      link.href = '/favicon.ico';
    }

  };

  this.updateVU = function(oSound) {

    if (soundManager.flashVersion >= 9 && self.config.useFavIcon && self.config.usePeakData) {
      me.setPageIcon(me.vuMeterData[parseInt(16*oSound.peakData.left, 10)][parseInt(16*oSound.peakData.right, 10)]);
    }

  };

  this.createVUData = function() {

    var i=0, j=0,
        canvas = me.vuDataCanvas.getContext('2d'),
        vuGrad = canvas.createLinearGradient(0, 16, 0, 0),
        bgGrad = canvas.createLinearGradient(0, 16, 0, 0),
        outline = 'rgba(0,0,0,0.2)';

    vuGrad.addColorStop(0,'rgb(0,192,0)');
    vuGrad.addColorStop(0.30,'rgb(0,255,0)');
    vuGrad.addColorStop(0.625,'rgb(255,255,0)');
    vuGrad.addColorStop(0.85,'rgb(255,0,0)');
    bgGrad.addColorStop(0,outline);
    bgGrad.addColorStop(1,'rgba(0,0,0,0.5)');
    for (i=0; i<16; i++) {
      me.vuMeterData[i] = [];
    }
    for (i=0; i<16; i++) {
      for (j=0; j<16; j++) {
        // reset/erase canvas
        me.vuDataCanvas.setAttribute('width',16);
        me.vuDataCanvas.setAttribute('height',16);
        // draw new stuffs
        canvas.fillStyle = bgGrad;
        canvas.fillRect(0,0,7,15);
        canvas.fillRect(8,0,7,15);
        /*
        // shadow
        canvas.fillStyle = 'rgba(0,0,0,0.1)';
        canvas.fillRect(1,15-i,7,17-(17-i));
        canvas.fillRect(9,15-j,7,17-(17-j));
        */
        canvas.fillStyle = vuGrad;
        canvas.fillRect(0,15-i,7,16-(16-i));
        canvas.fillRect(8,15-j,7,16-(16-j));
        // and now, clear out some bits.
        canvas.clearRect(0,3,16,1);
        canvas.clearRect(0,7,16,1);
        canvas.clearRect(0,11,16,1);
        me.vuMeterData[i][j] = me.vuDataCanvas.toDataURL('image/png');
        // for debugging VU images
        /*
        var o = document.createElement('img');
        o.style.marginRight = '5px'; 
        o.src = vuMeterData[i][j];
        document.documentElement.appendChild(o);
        */
      }
    }

  };

  this.testCanvas = function() {

    // canvas + toDataURL();
    var c = document.createElement('canvas'),
        ctx = null, ok;
    if (!c || typeof c.getContext === 'undefined') {
      return null;
    }
    ctx = c.getContext('2d');
    if (!ctx || typeof c.toDataURL !== 'function') {
      return null;
    }
    // just in case..
    try {
      ok = c.toDataURL('image/png');
    } catch(e) {
      // no canvas or no toDataURL()
      return null;
    }
    // assume we're all good.
    return c;

  };

  this.init = function() {

    if (self.config.useFavIcon) {
      me.vuDataCanvas = me.testCanvas();
      if (me.vuDataCanvas && (isFirefox || isOpera)) {
        // these browsers support dynamically-updating the favicon
        me.createVUData();
      } else {
        // browser doesn't support doing this
        self.config.useFavIcon = false;
      }
    }

  };

  this.init();

};

// completely optional: Metadata/annotations/segments code

ThreeSixtyPlayer.prototype.Metadata = function(oSound, oParent) {

  soundManager._wD('Metadata()');

  var me = this,
      oBox = oSound._360data.oUI360,
      o = oBox.getElementsByTagName('ul')[0],
      oItems = o.getElementsByTagName('li'),
      isFirefox = (navigator.userAgent.match(/firefox/i)),
      isAlt = false, i, oDuration;

  this.lastWPExec = 0;
  this.refreshInterval = 250;
  this.totalTime = 0;

  this.events = {

    whileplaying: function() {

      var width = oSound._360data.width,
          radius = oSound._360data.radius,
          fullDuration = (oSound.durationEstimate||(me.totalTime*1000)),
          isAlt = null, i, j, d;

      for (i=0,j=me.data.length; i<j; i++) {
        isAlt = (i%2===0);
        oParent.drawSolidArc(oSound._360data.oCanvas,(isAlt?oParent.config.segmentRingColorAlt:oParent.config.segmentRingColor),isAlt?width:width, isAlt?radius/2:radius/2, oParent.deg2rad(360*(me.data[i].endTimeMS/fullDuration)), oParent.deg2rad(360*((me.data[i].startTimeMS||1)/fullDuration)), true);
      }
      d = new Date();
      if (d-me.lastWPExec>me.refreshInterval) {
        me.refresh();
        me.lastWPExec = d;
      }

    }

  };

  this.refresh = function() {

    // Display info as appropriate
    var i, j, index = null,
        now = oSound.position,
        metadata = oSound._360data.metadata.data;

    for (i=0, j=metadata.length; i<j; i++) {
      if (now >= metadata[i].startTimeMS && now <= metadata[i].endTimeMS) {
        index = i;
        break;
      }
    }
    if (index !== metadata.currentItem && index < metadata.length) {
      // update
      oSound._360data.oLink.innerHTML = metadata.mainTitle+' <span class="metadata"><span class="sm2_divider"> | </span><span class="sm2_metadata">'+metadata[index].title+'</span></span>';
      // self.setPageTitle(metadata[index].title+' | '+metadata.mainTitle);
      metadata.currentItem = index;
    }

  };

  this.strToTime = function(sTime) {
    var segments = sTime.split(':'),
        seconds = 0, i;
    for (i=segments.length; i--;) {
      seconds += parseInt(segments[i], 10)*Math.pow(60,segments.length-1-i); // hours, minutes
    }
    return seconds;
  };

  this.data = [];
  this.data.givenDuration = null;
  this.data.currentItem = null;
  this.data.mainTitle = oSound._360data.oLink.innerHTML;

  for (i=0; i<oItems.length; i++) {
    this.data[i] = {
      o: null,
      title: oItems[i].getElementsByTagName('p')[0].innerHTML,
      startTime: oItems[i].getElementsByTagName('span')[0].innerHTML,
      startSeconds: me.strToTime(oItems[i].getElementsByTagName('span')[0].innerHTML.replace(/[()]/g,'')),
      duration: 0,
      durationMS: null,
      startTimeMS: null,
      endTimeMS: null,
      oNote: null
    };
  }
  oDuration = oParent.getElementsByClassName('duration','div',oBox);
  this.data.givenDuration = (oDuration.length?me.strToTime(oDuration[0].innerHTML)*1000:0);
  for (i=0; i<this.data.length; i++) {
    this.data[i].duration = parseInt(this.data[i+1]?this.data[i+1].startSeconds:(me.data.givenDuration?me.data.givenDuration:oSound.durationEstimate)/1000, 10)-this.data[i].startSeconds;
    this.data[i].startTimeMS = this.data[i].startSeconds*1000;
    this.data[i].durationMS = this.data[i].duration*1000;
    this.data[i].endTimeMS = this.data[i].startTimeMS+this.data[i].durationMS;
    this.totalTime += this.data[i].duration;
  }

};

if (navigator.userAgent.match(/webkit/i) && navigator.userAgent.match(/mobile/i)) {
  // iPad, iPhone etc.
  soundManager.setup({
    useHTML5Audio: true
  });
}

soundManager.setup({
  html5PollingInterval: 50, // increased framerate for whileplaying() etc.
  debugMode: true, // disable or enable debug output
  consoleOnly: true,
  flashVersion: 9,
  useHighPerformance: true,
  useFlashBlock: true
});

// FPS data, testing/debug only
if (soundManager.debugMode) {
  window.setInterval(function() {
    var p = window.threeSixtyPlayer;
    if (p && p.lastSound && p.lastSound._360data.fps && typeof window.isHome === 'undefined') {
      soundManager._writeDebug('fps: ~'+p.lastSound._360data.fps);
      p.lastSound._360data.fps = 0;
    }
  },1000);
}

window.ThreeSixtyPlayer = ThreeSixtyPlayer; // constructor

}(window));

threeSixtyPlayer = new ThreeSixtyPlayer();

// hook into SM2 init
soundManager.onready(threeSixtyPlayer.init);
