module.exports = {
  content: ['/home/claude/imoves-website/**/index.html', '/home/claude/imoves-website/404.html', '/home/claude/imoves-website/default/dist/js/app.js'],
  css: ['/home/claude/imoves-site/app.css.versiona'],
  // keep everything JS adds at runtime, plus whole component families
  safelist: {
    standard: ['open','ready','html','body','a','abbr','b','strong','small','sub','sup','hr','img','pre','code','kbd','samp','button','input','optgroup','select','textarea','fieldset','legend','progress','details','summary','template','blockquote','dd','dl','dt','figure','figcaption','h1','h2','h3','h4','h5','h6','p','ul','ol','li','table','th','td','thead','tbody','tr','iframe','video','audio','svg','canvas','picture','source','label','main','nav','header','footer','section','article','aside','span','div','em','i','u','s','cite','q','address','time','mark','br','visible','fixed','hidden','opacity-0','no-csstransforms3d','site-overlay','menu-btn','pushy-open-left','pushy-open-right','pushy-left','pushy-right','pushy-submenu-closed','pushy-submenu-open','pushy-open','pushy-active','pushy-content','pushy-submenu','container-push','push','push-right','push-left','wistia_embed','wistia_responsive_padding','wistia_responsive_wrapper','wistia_async','iframe','slick-active','slick-current','slick-slide','slick-track','slick-list','slick-dots','is-active','is-open','in','show','collapse','collapsing','fade'],
    deep: [/^mfp-/, /^pushy/, /^wistia/, /^text-content/],
    greedy: [/data-video-modal/, /mfp/],
    // keep every bare element selector (the CSS reset relies on them)
    standardElements: true,
  },
  defaultExtractor: content => content.match(/[\w-/:%.@!]+(?<!:)/g) || [],
  variables: false,
  fontFace: false,
  keyframes: false,
};
