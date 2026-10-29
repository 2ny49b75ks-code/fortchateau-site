/* Menu mobile, filtre du catalogue, un seul lecteur audio à la fois. */
(function () {
  var t = document.querySelector('.nav-toggle'), n = document.getElementById('main-nav');
  if (t && n) t.addEventListener('click', function () { var o = n.classList.toggle('open'); t.setAttribute('aria-expanded', o ? 'true' : 'false'); });

  var q = document.getElementById('q'), cards = [].slice.call(document.querySelectorAll('.site')), chips = [].slice.call(document.querySelectorAll('.chip'));
  if (q && cards.length) {
    var cont = 'all', out = document.getElementById('count'), tpl = out ? out.getAttribute('data-tpl') : '', tpl1 = out ? out.getAttribute('data-tpl1') : '';
    var norm = function (s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
    var run = function () {
      var v = norm(q.value.trim()), shown = 0;
      cards.forEach(function (c) {
        var ok = (cont === 'all' || c.getAttribute('data-c') === cont) && (!v || c.getAttribute('data-s').indexOf(v) > -1);
        c.classList.toggle('hidden', !ok); if (ok) shown++;
      });
      [].forEach.call(document.querySelectorAll('.country'), function (b) { b.classList.toggle('hidden', !b.querySelector('.site:not(.hidden)')); });
      [].forEach.call(document.querySelectorAll('.continent'), function (b) { b.classList.toggle('hidden', !b.querySelector('.site:not(.hidden)')); });
      if (out) out.textContent = (shown === 1 && tpl1 ? tpl1 : tpl).replace('{n}', shown);
    };
    q.addEventListener('input', run);
    chips.forEach(function (c) { c.addEventListener('click', function () { cont = c.getAttribute('data-c'); chips.forEach(function (x) { x.classList.toggle('on', x === c); }); run(); }); });
    run();
  }

  var audios = [].slice.call(document.querySelectorAll('audio'));
  audios.forEach(function (a) { a.addEventListener('play', function () { audios.forEach(function (o) { if (o !== a) o.pause(); }); }); });
})();
