// Version C: Cloudflare Stream lightbox player
(function(){
  var CUSTOMER='customer-q4gm0gw925cd2f03.cloudflarestream.com';
  function open(uid,title){
    var lb=document.createElement('div');lb.className='cf-lightbox';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');lb.setAttribute('aria-label',title||'Video');
    var inner=document.createElement('div');inner.className='cf-lightbox-inner';
    var close=document.createElement('button');close.className='cf-lightbox-close';close.setAttribute('aria-label','Close video');close.innerHTML='&times;';
    var f=document.createElement('iframe');
    f.src='https://'+CUSTOMER+'/'+uid+'/iframe?autoplay=true&preload=true';
    f.allow='accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';f.setAttribute('allowfullscreen','');f.title=title||'Video';
    inner.appendChild(close);inner.appendChild(f);lb.appendChild(inner);document.body.appendChild(lb);
    document.body.style.overflow='hidden';
    requestAnimationFrame(function(){lb.classList.add('is-open');});
    function shut(){lb.classList.remove('is-open');document.body.style.overflow='';setTimeout(function(){lb.remove();},200);document.removeEventListener('keydown',esc);}
    function esc(e){if(e.key==='Escape')shut();}
    close.addEventListener('click',shut);
    lb.addEventListener('click',function(e){if(e.target===lb)shut();});
    document.addEventListener('keydown',esc);
    close.focus();
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.cf-video-thumb');if(!b)return;
    var v=b.closest('.cf-video');open(v.getAttribute('data-uid'),v.getAttribute('data-title'));
  });
})();
