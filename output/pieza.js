(function(){
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // tooltip generico para elementos con data-tooltip
  var tip = document.getElementById('tooltip');
  function bindTooltip(el){
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
  }
  if (tip){
    document.querySelectorAll('[data-tooltip]').forEach(bindTooltip);
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

  // Pictograma de personas (Parte I, id="picto-people"): en vez de tener un
  // set fijo de figuras que solo se reposicionan al cambiar de agrupacion,
  // se REPINTA por completo para cada modo, calculando la cantidad exacta
  // de figuras (enteras + una parcial recortada al final de cada categoria)
  // a partir de los conteos reales del SAT. Asi, "Todas juntas" siempre
  // muestra exactamente 60 figuras enteras + 177/500 de una figura mas
  // (30.177 personas / 500), sin fragmentos de mas ni de menos; y al
  // agrupar por sexo o por franja etaria, cada grupo termina con una unica
  // figura recortada propia, en vez de heredar los cortes de otro modo.
  var PEOPLE_PER_ICON = 1000;
  var PEOPLE_DATA = {
    total: 30177,
    bySex: { masc: 23842, fem: 6155, sindet: 180 },
    // cruce sexo x franja etaria (SAT, 2017-2024)
    cross: {
      '0-19':  { masc: 2458, fem: 1081, sindet: 4 },
      '20-34': { masc: 8774, fem: 2016, sindet: 8 },
      '35-49': { masc: 4959, fem: 1279, sindet: 0 },
      '50-64': { masc: 3337, fem: 903,  sindet: 1 },
      '65+':   { masc: 3407, fem: 671,  sindet: 0 },
      'sindet':{ masc: 907,  fem: 205,  sindet: 167 }
    }
  };

  function formatCount(n){ return formatNum(n, 0); }

  // Texto del tooltip para TODAS las figuras de una categoria: cuantos
  // hombres y mujeres hay ahi (y sin determinar, si corresponde), salvo en
  // "todas juntas" que muestra el total general.
  function categoryTooltip(mode, key){
    if (mode === 'sex'){
      if (key === 'masc') return formatCount(PEOPLE_DATA.bySex.masc) + ' hombres';
      if (key === 'fem') return formatCount(PEOPLE_DATA.bySex.fem) + ' mujeres';
      return formatCount(PEOPLE_DATA.bySex.sindet) + ' personas sin sexo determinado';
    }
    if (mode === 'edad'){
      var c = PEOPLE_DATA.cross[key];
      var parts = [formatCount(c.masc) + ' hombres', formatCount(c.fem) + ' mujeres'];
      if (c.sindet > 0) parts.push(formatCount(c.sindet) + ' sin determinar');
      return parts.join(', ');
    }
    return formatCount(PEOPLE_DATA.total) + ' personas';
  }

  // Constantes de agrupacion/color compartidas por los dos pictogramas y por
  // layoutPictogram. Van ARRIBA (antes de renderPeoplePictogram/
  // renderEmsePictogram) porque reserveMaxHeight necesita poder recorrer
  // los modos "sex"/"edad"/"soledad" desde el arranque, antes de que se
  // capturen las figuras para la animacion de aparicion (mas abajo).
  var OUTCOME_COLOR = { intento: 'var(--accent-warm)', idea_sin: 'var(--accent-cool)', ninguno: 'var(--bar-neutral)' };
  var SEX_ORDER = ['masc','fem'];
  var SEX_ORDER_SINDET = ['masc','fem','sindet'];
  var EDAD_ORDER = ['0-19','20-34','35-49','50-64','65+','sindet'];
  var SOLEDAD_ORDER = ['nunca','rara_vez','algunas_veces','casi_siempre','siempre'];
  var PERSON_COLOR = { masc: 'var(--accent-masc)', fem: 'var(--accent-fem)', sindet: 'var(--muted)' };
  var GROUP_LABEL = {
    masc: 'Hombres', fem: 'Mujeres', sindet: 'Sin determinar',
    '0-19':'0-19', '20-34':'20-34', '35-49':'35-49', '50-64':'50-64', '65+':'65+',
    nunca: 'Nunca', rara_vez: 'Rara vez', algunas_veces: 'Algunas veces', casi_siempre: 'Casi siempre', siempre: 'Siempre'
  };

  // attrs: objeto plano {nombreEnCamelCase: valor} -> se vuelca como
  // data-nombre-en-camel-case en el span (dataset hace la conversion sola).
  function makePersonSpan(attrs, startFrac, endFrac, slot, tooltip){
    var span = document.createElement('span');
    span.className = 'picto-person';
    Object.keys(attrs || {}).forEach(function(k){
      var v = attrs[k];
      if (v !== null && v !== undefined) span.dataset[k] = v;
    });
    span.dataset.slot = slot;
    if (tooltip){
      span.setAttribute('data-tooltip', tooltip);
      span.tabIndex = 0;
      if (tip) bindTooltip(span);
    }
    if (startFrac > 0 || endFrac < 1){
      span.classList.add('partial');
      var leftPct = (startFrac * 100).toFixed(2);
      var rightPct = ((1 - endFrac) * 100).toFixed(2);
      span.style.clipPath = 'inset(0 ' + rightPct + '% 0 ' + leftPct + '%)';
    }
    return span;
  }

  // Encadena los sub-conteos (por ejemplo, masc/fem/sindet dentro de una
  // franja etaria) en una sola linea continua de personas, cortada cada
  // PEOPLE_PER_ICON: cada figura entera representa exactamente 500
  // personas, y solo la ULTIMA figura de esta categoria queda parcial
  // (recortada al resto exacto). El "cursor" arranca en 0 para cada
  // categoria, asi los cortes de una categoria nunca se mezclan con los
  // de otra.
  //
  // Cuando un corte de sexo cae en el medio de una figura (por ejemplo, la
  // figura numero 5 es 91,6% hombres y 8,4% mujeres), esa figura se arma con
  // 2 <span> con el mismo "slot": layoutPictogram los coloca superpuestos en
  // la misma celda, cada uno mostrando (via clip-path) solo su franja, para
  // que sigan pareciendo una unica figura y no infle el ancho del grupo.
  // subcounts: [{ attrs: {...}, count: N }, ...], encadenados en una sola
  // linea continua cortada cada perIcon unidades (persona=1000, o
  // punto-porcentual=1 para la EMSE). tooltip es el mismo para todos los
  // fragmentos de esta categoria (asi el "cursor" arranca en 0).
  function buildCategoryIcons(subcounts, tooltip, perIcon){
    var icons = [];
    var cursor = 0;
    var slot = 0;
    subcounts.forEach(function(sc){
      var remaining = sc.count;
      while (remaining > 0){
        var space = perIcon - cursor;
        var take = Math.min(remaining, space);
        var startFrac = cursor / perIcon;
        var endFrac = (cursor + take) / perIcon;
        icons.push(makePersonSpan(sc.attrs, startFrac, endFrac, slot, tooltip));
        remaining -= take;
        cursor += take;
        if (cursor >= perIcon) { cursor = 0; slot++; }
      }
    });
    return icons;
  }

  function renderPeoplePictogram(grid, mode){
    var icons;
    if (mode === 'sex'){
      icons = [];
      SEX_ORDER_SINDET.forEach(function(sex){
        icons = icons.concat(buildCategoryIcons(
          [{ attrs: { sex: sex }, count: PEOPLE_DATA.bySex[sex] }],
          categoryTooltip('sex', sex), PEOPLE_PER_ICON
        ));
      });
    } else if (mode === 'edad'){
      icons = [];
      EDAD_ORDER.forEach(function(edad){
        var c = PEOPLE_DATA.cross[edad];
        icons = icons.concat(buildCategoryIcons([
          { attrs: { sex: 'masc', edad: edad }, count: c.masc },
          { attrs: { sex: 'fem', edad: edad }, count: c.fem },
          { attrs: { sex: 'sindet', edad: edad }, count: c.sindet }
        ], categoryTooltip('edad', edad), PEOPLE_PER_ICON));
      });
    } else {
      icons = buildCategoryIcons([{ attrs: {}, count: PEOPLE_DATA.total }], categoryTooltip('none'), PEOPLE_PER_ICON);
    }
    grid.querySelectorAll('.picto-person').forEach(function(el){ el.remove(); });
    icons.forEach(function(icon){ grid.appendChild(icon); });
  }

  var peopleGrid = document.getElementById('picto-people');
  if (peopleGrid) reserveMaxHeight(peopleGrid, renderPeoplePictogram, ['none', 'sex', 'edad']);

  // Pictograma de la EMSE (Parte III, id="picto-emse"): mismo criterio que
  // el de arriba. Los datos son porcentajes ponderados (EMSE 2018, n=56.981
  // estudiantes) que ya suman exactamente 100 por construccion; el "cursor"
  // de PEOPLE_PER_ICON=1 (1 figura = 1 punto porcentual) se resetea en cada
  // categoria del modo activo (todos/sexo/frecuencia de soledad), y dentro
  // de cada una se encadena por resultado (intento/ideacion sin intento/
  // ninguna), pintando la fraccion exacta.
  var EMSE_PER_ICON = 5;
  var EMSE_DATA = {
    total: 56981,
    none: { intento: 14.758284, idea_sin: 10.326548, ninguno: 74.915168 },
    sex: {
      masc: { intento: 4.889288, idea_sin: 3.692205, ninguno: 39.446252 },
      fem:  { intento: 9.796441, idea_sin: 6.667050,  ninguno: 35.508764 }
    },
    soledad: {
      nunca:         { intento: 2.110849, idea_sin: 1.487539, ninguno: 28.520240 },
      rara_vez:      { intento: 2.395027, idea_sin: 1.672723, ninguno: 20.663324 },
      algunas_veces: { intento: 4.054958, idea_sin: 3.480206, ninguno: 18.870027 },
      casi_siempre:  { intento: 3.533936, idea_sin: 2.471330, ninguno: 5.308849 },
      siempre:       { intento: 2.636313, idea_sin: 1.206244, ninguno: 1.588434 }
    }
  };
  var OUTCOME_LABEL = { intento: 'intentaron suicidarse', idea_sin: 'tuvieron ideación sin intento', ninguno: 'ninguna de las dos' };

  function pctLabel(n){ return n.toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }

  // % que representa este grupo (sexo o frecuencia de soledad) sobre el
  // total de estudiantes (para el rotulo del grupo, "Hombres (48%)").
  function emseGroupShare(mode, key){
    var d = mode === 'sex' ? EMSE_DATA.sex[key] : EMSE_DATA.soledad[key];
    return Math.round(d.intento + d.idea_sin + d.ninguno);
  }

  // Los 3 resultados (intento/idea_sin/ninguno) EXPRESADOS COMO % de ESE
  // grupo en particular (suman 100 entre los 3), en vez de su % sobre el
  // total general de estudiantes.
  function emseConditional(mode, key){
    var d = mode === 'sex' ? EMSE_DATA.sex[key] : EMSE_DATA.soledad[key];
    var total = d.intento + d.idea_sin + d.ninguno;
    return {
      intento: d.intento / total * 100,
      idea_sin: d.idea_sin / total * 100,
      ninguno: d.ninguno / total * 100
    };
  }

  function emseTooltip(mode, key){
    var d = mode === 'none' ? EMSE_DATA.none : emseConditional(mode, key);
    return ['intento', 'idea_sin', 'ninguno'].map(function(o){ return pctLabel(d[o]) + ' ' + OUTCOME_LABEL[o]; }).join('\n');
  }

  function renderEmsePictogram(grid, mode){
    var icons = [];
    var attrKey = mode === 'sex' ? 'sexmodeGroup' : (mode === 'soledad' ? 'soledadmodeGroup' : null);
    var outcomeKey = mode === 'sex' ? 'sexmodeOutcome' : (mode === 'soledad' ? 'soledadmodeOutcome' : 'nonemodeOutcome');
    if (mode === 'sex' || mode === 'soledad'){
      var order = mode === 'sex' ? SEX_ORDER : SOLEDAD_ORDER;
      order.forEach(function(key){
        // Cada grupo se pinta relativo a si mismo (los 3 resultados suman
        // 100% de ESE grupo), asi todos los grupos quedan igual de "anchos"
        // y el rotulo (con el % real que representa ese grupo sobre el
        // total) es lo que muestra su tamano real.
        var d = emseConditional(mode, key);
        var attrsFor = function(outcome){
          var a = {}; a[attrKey] = key; a[outcomeKey] = outcome; return a;
        };
        icons = icons.concat(buildCategoryIcons([
          { attrs: attrsFor('intento'), count: d.intento },
          { attrs: attrsFor('idea_sin'), count: d.idea_sin },
          { attrs: attrsFor('ninguno'), count: d.ninguno }
        ], emseTooltip(mode, key), EMSE_PER_ICON));
      });
    } else {
      var d0 = EMSE_DATA.none;
      var attrsFor0 = function(outcome){ var a = {}; a[outcomeKey] = outcome; return a; };
      icons = buildCategoryIcons([
        { attrs: attrsFor0('intento'), count: d0.intento },
        { attrs: attrsFor0('idea_sin'), count: d0.idea_sin },
        { attrs: attrsFor0('ninguno'), count: d0.ninguno }
      ], emseTooltip('none'), EMSE_PER_ICON);
    }
    grid.querySelectorAll('.picto-person').forEach(function(el){ el.remove(); });
    icons.forEach(function(icon){ grid.appendChild(icon); });
  }

  var emseGrid = document.getElementById('picto-emse');
  if (emseGrid) reserveMaxHeight(emseGrid, renderEmsePictogram, ['none', 'sex', 'soledad']);

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
  function layoutPictogram(grid, mode){
    var isEmse = grid.id === 'picto-emse';
    var icons = Array.prototype.slice.call(grid.querySelectorAll('.picto-person'));
    grid.querySelectorAll('.picto-row-label').forEach(function(l){ l.remove(); });
    var iconW = 14, iconH = 20, colGap = 4, rowGap = 14, lineGap = 6;
    var labelW = isEmse && (mode === 'sex' || mode === 'soledad') ? 168 : 130;
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
      // Dos (o mas) fragmentos pueden compartir el mismo "slot" (la misma
      // figura de 500 personas, partida por color); en ese caso van
      // superpuestos en una unica celda en vez de una cada uno, para que el
      // corte de sexo no infle el ancho del grupo.
      var slotPos = {};
      var nextPos = 0;
      items.forEach(function(icon, i){
        var s = icon.dataset.slot !== undefined ? ('s' + icon.dataset.slot) : ('i' + i);
        if (!(s in slotPos)) slotPos[s] = nextPos++;
      });
      var lines = Math.ceil(nextPos / maxCols);
      var blockH = lines * (iconH + lineGap) - lineGap;
      if (labelW){
        var label = document.createElement('div');
        label.className = 'picto-row-label';
        label.textContent = g === 'all'
          ? (isEmse ? 'Total (' + formatCount(EMSE_DATA.total) + ')' : 'Total')
          : (isEmse && (mode === 'sex' || mode === 'soledad')) ? (GROUP_LABEL[g] || g) + ' (' + emseGroupShare(mode, g) + '%)' : (GROUP_LABEL[g] || g);
        label.style.top = (y + blockH/2 - 8) + 'px';
        label.style.width = labelW + 'px';
        grid.appendChild(label);
      }
      items.forEach(function(icon, i){
        var s = icon.dataset.slot !== undefined ? ('s' + icon.dataset.slot) : ('i' + i);
        var pos = slotPos[s];
        var col = pos % maxCols;
        var line = Math.floor(pos / maxCols);
        var left = labelW + col * (iconW + colGap);
        var top = y + line * (iconH + lineGap);
        icon.style.left = left + 'px';
        icon.style.top = top + 'px';
        icon.style.backgroundColor = colorOf(icon);
      });
      y += blockH + rowGap;
    });
    // La altura se "reserva" al maximo que haya necesitado alguna vez este
    // grid (ver reserveMaxHeight): asi cambiar de agrupacion no corre el
    // resto de la pagina para arriba/abajo, aunque el modo nuevo use menos
    // espacio que el anterior.
    var contentH = y - rowGap;
    var reservedH = parseFloat(grid.dataset.reservedH || '0');
    if (contentH > reservedH){ reservedH = contentH; grid.dataset.reservedH = reservedH; }
    grid.style.height = reservedH + 'px';

    // Si este modo ocupa menos que el espacio reservado, centrar todo el
    // contenido (figuras + rotulos) dentro de ese espacio fijo, en vez de
    // dejarlo pegado arriba con el sobrante vacio abajo.
    var yOffset = (reservedH - contentH) / 2;
    if (yOffset > 0){
      grid.querySelectorAll('.picto-person, .picto-row-label').forEach(function(el){
        el.style.top = (parseFloat(el.style.top) + yOffset) + 'px';
      });
    }
  }

  document.querySelectorAll('.mode-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var group = btn.parentElement;
      var wrap = group.nextElementSibling;
      var grid = wrap.querySelector('.picto-grid');
      group.querySelectorAll('.mode-btn').forEach(function(b){ b.classList.remove('selected'); });
      btn.classList.add('selected');
      var mode = btn.dataset.mode;
      if (grid.id === 'picto-people' || grid.id === 'picto-emse'){
        if (grid.id === 'picto-people') renderPeoplePictogram(grid, mode);
        else renderEmsePictogram(grid, mode);
        grid.querySelectorAll('.picto-person').forEach(function(p){ p.classList.add('shown'); });
      }
      layoutPictogram(grid, mode);
      wrap.querySelectorAll('.picto-legend-block').forEach(function(lb){
        lb.classList.toggle('active', lb.dataset.legend === mode);
      });
    });
  });
  // Recorre todos los modos de un pictograma una sola vez (sin que se note,
  // es sincronico y termina dejando el grid en "none" antes de pintar) para
  // que grid.dataset.reservedH quede establecido en el maximo desde el
  // arranque, y el primer cambio de agrupacion no mueva la pagina.
  function reserveMaxHeight(grid, renderFn, modes){
    modes.forEach(function(mode){
      renderFn(grid, mode);
      layoutPictogram(grid, mode);
    });
    renderFn(grid, 'none');
    layoutPictogram(grid, 'none');
  }

  window.addEventListener('resize', function(){
    document.querySelectorAll('.mode-btn.selected').forEach(function(btn){
      var wrap = btn.parentElement.nextElementSibling;
      var grid = wrap.querySelector('.picto-grid');
      layoutPictogram(grid, btn.dataset.mode);
    });
  });

})();
