(function(){
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // tooltip generico para elementos con data-tooltip
  var tip = document.getElementById('tooltip');
  if (tip){
    document.querySelectorAll('[data-tooltip]').forEach(function(el){
      el.addEventListener('mouseenter', function(ev){
        tip.textContent = el.getAttribute('data-tooltip');
        tip.hidden = false;
        requestAnimationFrame(function(){ tip.classList.add('shown'); });
      });
      el.addEventListener('mousemove', function(ev){
        var x = ev.clientX + 14, y = ev.clientY + 16;
        if (x + 260 > window.innerWidth) x = ev.clientX - 260 - 14;
        tip.style.left = x + 'px';
        tip.style.top = y + 'px';
      });
      el.addEventListener('mouseleave', function(){
        tip.classList.remove('shown');
        tip.hidden = true;
      });
      el.addEventListener('focus', function(){
        var r = el.getBoundingClientRect();
        tip.textContent = el.getAttribute('data-tooltip');
        tip.style.left = (r.left) + 'px';
        tip.style.top = (r.bottom + 8) + 'px';
        tip.hidden = false;
        tip.classList.add('shown');
      });
      el.addEventListener('blur', function(){ tip.classList.remove('shown'); tip.hidden = true; });
    });
  }

  var revealEls = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealEls.forEach(function(el){ el.classList.add('in-view'); });
  } else {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add('in-view'); io.unobserve(e.target); }
      });
    }, { threshold: 0.18 });
    revealEls.forEach(function(el){ io.observe(el); });
  }

  function formatNum(val, decimals){
    return val.toLocaleString('es-AR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }
  function animateCount(el){
    var target = parseFloat(el.dataset.count);
    var decimals = el.dataset.decimals ? parseInt(el.dataset.decimals, 10) : 0;
    var suffix = el.dataset.suffix || '';
    var dur = 1300, start = null;
    function frame(ts){
      if (start === null) start = ts;
      var p = Math.min(1, (ts - start) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = formatNum(target * eased, decimals) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var countEls = document.querySelectorAll('[data-count]');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    countEls.forEach(function(el){
      var target = parseFloat(el.dataset.count);
      var decimals = el.dataset.decimals ? parseInt(el.dataset.decimals, 10) : 0;
      el.textContent = formatNum(target, decimals) + (el.dataset.suffix || '');
    });
  } else {
    var io2 = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { animateCount(e.target); io2.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    countEls.forEach(function(el){ io2.observe(el); });
  }

  document.querySelectorAll('.picto-grid').forEach(function(grid){
    var people = grid.querySelectorAll('.picto-person');
    if (reduceMotion || !('IntersectionObserver' in window)) {
      people.forEach(function(p){ p.classList.add('shown'); });
      return;
    }
    var io3 = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) {
          people.forEach(function(p, i){ setTimeout(function(){ p.classList.add('shown'); }, i * 11); });
          io3.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    io3.observe(grid);
  });

  document.querySelectorAll('.chart-line').forEach(function(path){
    var len = path.getTotalLength();
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = reduceMotion ? 0 : len;
    if (reduceMotion || !('IntersectionObserver' in window)) return;
    var io4 = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { path.style.strokeDashoffset = 0; io4.unobserve(e.target); }
      });
    }, { threshold: 0.35 });
    io4.observe(path);
  });

  document.querySelectorAll('.chart-bars').forEach(function(svgFig){
    var bars = svgFig.querySelectorAll('.bar-grow');
    if (reduceMotion || !('IntersectionObserver' in window)) return;
    var io5 = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) {
          bars.forEach(function(b, i){ setTimeout(function(){ b.classList.add('grown'); }, i * 70); });
          io5.unobserve(e.target);
        }
      });
    }, { threshold: 0.25 });
    io5.observe(svgFig);
  });

  // quiz: el boton de revelar solo aparece cuando TODAS las preguntas del cuadro fueron respondidas
  document.querySelectorAll('.quiz').forEach(function(quiz){
    var groups = quiz.querySelectorAll('.quiz-options');
    var revealBtn = quiz.querySelector('.quiz-reveal-btn');
    function checkAllAnswered(){
      var allAnswered = true;
      groups.forEach(function(g){ if (!g.querySelector('.quiz-btn.selected')) allAnswered = false; });
      if (revealBtn) revealBtn.hidden = !allAnswered;
    }
    groups.forEach(function(group){
      var btns = group.querySelectorAll('.quiz-btn');
      btns.forEach(function(btn){
        btn.addEventListener('click', function(){
          btns.forEach(function(b){ b.classList.remove('selected'); });
          btn.classList.add('selected');
          checkAllAnswered();
        });
      });
    });
  });
  document.querySelectorAll('.quiz-reveal-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var target = document.getElementById(btn.dataset.target);
      if (!target) return;
      target.hidden = !target.hidden;
      btn.textContent = target.hidden ? btn.textContent.replace('Ocultar', 'Ver') : btn.textContent.replace('Ver', 'Ocultar');
      if (!target.hidden){
        target.querySelectorAll('.bar-grow').forEach(function(b, i){ setTimeout(function(){ b.classList.add('grown'); }, i*70); });
        target.querySelectorAll('.picto-grid').forEach(function(grid){
          grid.querySelectorAll('.picto-person').forEach(function(p, i){ setTimeout(function(){ p.classList.add('shown'); }, i*7); });
        });
        target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
      }
    });
  });

  // toggle SAT/DEIS en el grafico de casos por año
  var toggleSat = document.getElementById('toggle-sat');
  var toggleDeis = document.getElementById('toggle-deis');
  var deisAside = document.getElementById('deis-aside');
  function updateSeries(){
    document.querySelectorAll('[data-series="sat"]').forEach(function(el){ el.setAttribute('data-hidden', toggleSat.checked ? '0' : '1'); });
    document.querySelectorAll('[data-series="deis"]').forEach(function(el){ el.setAttribute('data-hidden', toggleDeis.checked ? '0' : '1'); });
    if (deisAside) deisAside.hidden = !toggleDeis.checked;
  }
  if (toggleSat && toggleDeis){
    toggleSat.addEventListener('change', updateSeries);
    toggleDeis.addEventListener('change', updateSeries);
  }

  // toggle de agrupacion del pictograma (sexo / soledad), tipo histograma horizontal animado
  var OUTCOME_COLOR = { intento: 'var(--accent-warm)', idea_sin: 'var(--accent-cool)', ninguno: 'var(--bar-neutral)' };
  var SEX_ORDER = ['masc','fem'];
  var SEX_ORDER_SINDET = ['masc','fem','sindet'];
  var EDAD_ORDER = ['0-19','20-34','35-49','50-64','65+','sindet'];
  var SOLEDAD_ORDER = ['nunca','rara_vez','algunas_veces','casi_siempre','siempre'];
  var PERSON_COLOR = { masc: 'var(--accent-masc)', fem: 'var(--accent-fem)', sindet: 'var(--muted)' };
  var GROUP_LABEL = {
    masc: 'Varones', fem: 'Mujeres', sindet: 'Sin determinar',
    '0-19':'0-19', '20-34':'20-34', '35-49':'35-49', '50-64':'50-64', '65+':'65+',
    nunca: 'Nunca', rara_vez: 'Rara vez', algunas_veces: 'Algunas veces', casi_siempre: 'Casi siempre', siempre: 'Siempre'
  };

  function layoutPictogram(grid, mode){
    var isEmse = grid.id === 'picto-emse';
    var icons = Array.prototype.slice.call(grid.querySelectorAll('.picto-person'));
    grid.querySelectorAll('.picto-row-label').forEach(function(l){ l.remove(); });
    var iconW = 14, iconH = 20, colGap = 4, rowGap = 14, lineGap = 6;
    var labelW = mode === 'none' ? 0 : 130;
    var containerW = grid.parentElement.clientWidth || 640;
    var maxCols = Math.max(4, Math.floor((containerW - labelW) / (iconW + colGap)));

    var groupsOrder;
    if (isEmse) groupsOrder = mode === 'sex' ? SEX_ORDER : (mode === 'soledad' ? SOLEDAD_ORDER : ['all']);
    else groupsOrder = mode === 'sex' ? SEX_ORDER_SINDET : (mode === 'edad' ? EDAD_ORDER : ['all']);

    function groupOf(icon){
      if (isEmse){
        if (mode === 'sex') return icon.dataset.sexmodeGroup;
        if (mode === 'soledad') return icon.dataset.soledadmodeGroup;
        return 'all';
      }
      if (mode === 'sex') return icon.dataset.sex;
      if (mode === 'edad') return icon.dataset.edad;
      return 'all';
    }
    function colorOf(icon){
      if (isEmse){
        var outcome = mode === 'sex' ? icon.dataset.sexmodeOutcome : (mode === 'soledad' ? icon.dataset.soledadmodeOutcome : icon.dataset.nonemodeOutcome);
        return OUTCOME_COLOR[outcome];
      }
      if (mode === 'none') return '';
      return PERSON_COLOR[icon.dataset.sex];
    }
    var buckets = {};
    groupsOrder.forEach(function(g){ buckets[g] = []; });
    icons.forEach(function(icon){
      var g = groupOf(icon);
      if (!buckets[g]) buckets[g] = [];
      buckets[g].push(icon);
    });

    var y = 0;
    groupsOrder.forEach(function(g){
      var items = buckets[g];
      if (!items.length) return;
      var lines = Math.ceil(items.length / maxCols);
      var blockH = lines * (iconH + lineGap) - lineGap;
      if (labelW){
        var label = document.createElement('div');
        label.className = 'picto-row-label';
        label.textContent = GROUP_LABEL[g] || g;
        label.style.top = (y + blockH/2 - 8) + 'px';
        label.style.width = labelW + 'px';
        grid.appendChild(label);
      }
      items.forEach(function(icon, i){
        var col = i % maxCols;
        var line = Math.floor(i / maxCols);
        var left = labelW + col * (iconW + colGap);
        var top = y + line * (iconH + lineGap);
        icon.style.left = left + 'px';
        icon.style.top = top + 'px';
        icon.style.backgroundColor = colorOf(icon);
      });
      y += blockH + rowGap;
    });
    grid.style.height = (y - rowGap) + 'px';
  }

  document.querySelectorAll('.mode-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var group = btn.parentElement;
      var wrap = group.nextElementSibling;
      var grid = wrap.querySelector('.picto-grid');
      group.querySelectorAll('.mode-btn').forEach(function(b){ b.classList.remove('selected'); });
      btn.classList.add('selected');
      var mode = btn.dataset.mode;
      layoutPictogram(grid, mode);
      wrap.querySelectorAll('.picto-legend-block').forEach(function(lb){
        lb.classList.toggle('active', lb.dataset.legend === mode);
      });
    });
  });
  // layout inicial (modo "none") una vez que las figuras esten listas para posicionarse
  document.querySelectorAll('#picto-emse, #picto-people').forEach(function(grid){ layoutPictogram(grid, 'none'); });
  window.addEventListener('resize', function(){
    document.querySelectorAll('.mode-btn.selected').forEach(function(btn){
      var wrap = btn.parentElement.nextElementSibling;
      var grid = wrap.querySelector('.picto-grid');
      layoutPictogram(grid, btn.dataset.mode);
    });
  });

})();
