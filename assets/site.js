/* prasannamalode.in — shared behaviour (no dependencies) */
(function () {
  'use strict';
  var root = document.documentElement;
  var ROOT = (document.body && document.body.getAttribute('data-root')) || '.';

  /* ---------- Theme ---------- */
  function setTheme(t) {
    if (t === 'system') { root.removeAttribute('data-theme'); try { localStorage.removeItem('theme'); } catch (e) {} }
    else { root.setAttribute('data-theme', t); try { localStorage.setItem('theme', t); } catch (e) {} }
  }
  function currentTheme() {
    var explicit = root.getAttribute('data-theme');
    if (explicit) return explicit;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest('.theme-toggle');
    if (!t) return;
    setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
  });

  /* ---------- Mobile menu ---------- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.menu-btn');
    var links = document.querySelector('.nav-links');
    if (btn && links) { var open = links.classList.toggle('open'); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); return; }
    if (links && links.classList.contains('open') && !e.target.closest('.nav')) links.classList.remove('open');
  });

  /* ---------- Toast ---------- */
  var toastEl;
  window.toast = function (msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastEl._t); toastEl._t = setTimeout(function () { toastEl.classList.remove('show'); }, 2200);
  };
  window.copyText = function (text, msg) {
    var done = function () { window.toast(msg || 'Copied to clipboard'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    else fallback();
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) { window.toast('Copy failed'); } document.body.removeChild(ta);
    }
  };
  window.escapeHtml = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };

  /* ---------- Article helpers (data comes from assets/articles-data.js) ---------- */
  var ARTICLES = window.ARTICLES || [];
  function fmtDate(a) { return a.display_date || a.date; }
  function articleHref(a) { return ROOT + '/' + a.file; }
  function card(a) {
    return '<a class="card card-link fade-up" href="' + articleHref(a) + '">' +
      '<span class="tag">' + escapeHtml(a.tag) + '</span>' +
      (a.series ? '<span class="row-series">Part ' + a.part + '</span>' : '') +
      '<h3>' + escapeHtml(a.title) + '</h3>' +
      '<p>' + escapeHtml(a.summary) + '</p>' +
      '<div class="card-meta"><span>' + escapeHtml(fmtDate(a)) + '</span><span class="dot"></span><span>' + escapeHtml(a.read) + '</span></div></a>';
  }
  function row(a) {
    return '<a class="row fade-up" href="' + articleHref(a) + '">' +
      '<div><span class="tag">' + escapeHtml(a.tag) + '</span>' +
      (a.series ? '<span class="row-series">' + escapeHtml(a.series) + ' · Part ' + a.part + '</span>' : '') +
      '<h3>' + escapeHtml(a.title) + '</h3><p>' + escapeHtml(a.summary) + '</p></div>' +
      '<div class="row-meta">' + escapeHtml(fmtDate(a)) + '<br>' + escapeHtml(a.read) + '</div></a>';
  }

  /* ---------- Index page: router + rendering ---------- */
  var SECTIONS = ['home', 'articles', 'tools', 'about'];
  function parseHash() {
    var h = (location.hash || '').replace(/^#\/?/, '');
    var parts = h.split('?');
    var name = parts[0] || 'home';
    var q = {};
    (parts[1] || '').split('&').forEach(function (kv) { if (!kv) return; var p = kv.split('='); q[decodeURIComponent(p[0])] = decodeURIComponent(p[1] || ''); });
    if (SECTIONS.indexOf(name) < 0) name = 'home';
    return { name: name, q: q };
  }
  var state = { query: '', tag: 'All' };
  function renderArticles() {
    var list = document.getElementById('articles-list');
    if (!list) return;
    var q = state.query.trim().toLowerCase();
    var items = ARTICLES.filter(function (a) {
      if (state.tag !== 'All' && a.tag !== state.tag && !(state.tag === 'Guides' && a.kind === 'guide')) return false;
      if (!q) return true;
      return (a.title + ' ' + a.summary + ' ' + a.tag + ' ' + (a.series || '')).toLowerCase().indexOf(q) >= 0;
    });
    list.innerHTML = items.length ? items.map(row).join('') : '<div class="empty">Nothing matches that search.</div>';
    var count = document.getElementById('articles-count');
    if (count) count.textContent = items.length + ' of ' + ARTICLES.length;
    document.querySelectorAll('.chip[data-tag]').forEach(function (c) { c.classList.toggle('active', c.getAttribute('data-tag') === state.tag); });
  }
  function initIndex() {
    var home = document.getElementById('home-articles-grid');
    if (!home) return; // not the index page
    var essays = ARTICLES.filter(function (a) { return a.kind !== 'guide'; });
    // Featured: newest essay large, plus two hand-picked pieces (featured: true) from other topics
    var newest = essays[0];
    var picks = essays.filter(function (a) { return a.featured && a !== newest; }).slice(0, 2);
    if (picks.length < 2) essays.filter(function (a) { return a !== newest && picks.indexOf(a) < 0 && a.tag !== newest.tag; }).slice(0, 2 - picks.length).forEach(function (a) { picks.push(a); });
    var mainHtml = newest ? '<a class="featured-main fade-up" href="' + articleHref(newest) + '">' +
      '<div class="kicker"><span class="tag">' + escapeHtml(newest.tag) + '</span><span class="new">Latest' + (newest.series ? ' · Part ' + newest.part + (newest.series ? ' of ' + ARTICLES.filter(function (x) { return x.series === newest.series; }).length : '') : '') + '</span></div>' +
      '<div class="featured-body"><h3>' + escapeHtml(newest.title) + '</h3><p>' + escapeHtml(newest.summary) + '</p>' +
      '<div class="card-meta"><span>' + escapeHtml(fmtDate(newest)) + '</span><span class="dot"></span><span>' + escapeHtml(newest.read) + '</span><span class="dot"></span><span class="read-on">Read the article →</span></div></div></a>' : '';
    home.innerHTML = mainHtml + '<div class="featured-side">' + picks.map(function (a, i) {
      return '<a class="card card-link fade-up d' + (i + 1) + '" href="' + articleHref(a) + '"><div class="eyebrow">Start here · ' + escapeHtml(a.tag) + '</div>' +
        '<h3 style="margin-top:0">' + escapeHtml(a.title) + '</h3><p>' + escapeHtml(a.summary) + '</p>' +
        '<div class="card-meta"><span>' + escapeHtml(fmtDate(a)) + '</span><span class="dot"></span><span>' + escapeHtml(a.read) + '</span></div></a>';
    }).join('') + '</div>';

    // Topics row with counts
    var topics = document.getElementById('topics');
    if (topics) {
      var counts = {};
      essays.forEach(function (a) { counts[a.tag] = (counts[a.tag] || 0) + 1; });
      var guides = ARTICLES.filter(function (a) { return a.kind === 'guide'; }).length;
      var order = Object.keys(counts).sort(function (x, y) { return counts[y] - counts[x] || x.localeCompare(y); });
      topics.innerHTML = order.map(function (t) { return '<a class="topic" href="#/articles?tag=' + encodeURIComponent(t) + '">' + escapeHtml(t) + '<span class="n">' + counts[t] + '</span></a>'; }).join('') +
        (guides ? '<a class="topic" href="#/articles?tag=Guides">Training guides<span class="n">' + guides + '</span></a>' : '');
    }

    // tag chips
    var tags = ['All'];
    ARTICLES.forEach(function (a) { if (a.kind !== 'guide' && tags.indexOf(a.tag) < 0) tags.push(a.tag); });
    if (ARTICLES.some(function (a) { return a.kind === 'guide'; })) tags.push('Guides');
    var filters = document.getElementById('article-filters');
    if (filters) filters.innerHTML = tags.map(function (t) { return '<button class="chip" data-tag="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>'; }).join('');
    document.addEventListener('click', function (e) {
      var c = e.target.closest('.chip[data-tag]'); if (!c) return;
      state.tag = c.getAttribute('data-tag'); renderArticles();
    });
    var search = document.getElementById('article-search');
    if (search) search.addEventListener('input', function () { state.query = search.value; renderArticles(); });

    var lastRoute = null;
    function route() {
      var r = parseHash();
      if (r.q.tag) state.tag = r.q.tag; else if (r.name === 'articles' && lastRoute !== 'articles') state.tag = 'All';
      if (r.q.q && search) { search.value = r.q.q; state.query = r.q.q; }
      SECTIONS.forEach(function (s) {
        var el = document.getElementById(s); if (el) el.hidden = s !== r.name;
        var nav = document.getElementById('nav-' + s); if (nav) { if (s === r.name) nav.setAttribute('aria-current', 'page'); else nav.removeAttribute('aria-current'); }
      });
      document.title = (r.name === 'home' ? '' : r.name.charAt(0).toUpperCase() + r.name.slice(1) + ' · ') + 'Prasanna Malode';
      renderArticles();
      lastRoute = r.name;
      var links = document.querySelector('.nav-links'); if (links) links.classList.remove('open');
      try { window.scrollTo(0, 0); } catch (e) {}
    }
    window.addEventListener('hashchange', route);
    route();
  }

  /* ---------- Article page: progress, TOC, scrollspy, share ---------- */
  function initArticle() {
    var prose = document.querySelector('.prose');
    if (!prose) return;
    var bar = document.querySelector('.progress');
    if (bar) {
      var onScroll = function () {
        var h = document.documentElement;
        var max = h.scrollHeight - h.clientHeight;
        bar.style.width = (max > 0 ? Math.min(100, (h.scrollTop / max) * 100) : 0) + '%';
      };
      window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
    }
    var heads = Array.prototype.slice.call(prose.querySelectorAll('h2'));
    var used = {};
    heads.forEach(function (h) {
      if (!h.id) {
        var id = h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'section';
        while (used[id]) id += '-2'; used[id] = 1; h.id = id;
      }
    });
    var tocs = document.querySelectorAll('[data-toc]');
    if (heads.length >= 2) {
      var html = '<ol>' + heads.map(function (h) { return '<li><a href="#' + h.id + '">' + escapeHtml(h.textContent) + '</a></li>'; }).join('') + '</ol>';
      Array.prototype.forEach.call(tocs, function (t) { t.querySelector('[data-toc-list]').innerHTML = html; });
    } else {
      Array.prototype.forEach.call(tocs, function (t) { t.hidden = true; });
    }
    if ('IntersectionObserver' in window && heads.length) {
      var links = document.querySelectorAll('.toc-side a');
      var active = null;
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) active = en.target.id; });
        links.forEach(function (l) { l.classList.toggle('active', l.getAttribute('href') === '#' + active); });
      }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 });
      heads.forEach(function (h) { io.observe(h); });
    }
    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-share]'); if (!b) return;
      var kind = b.getAttribute('data-share');
      var url = location.href.split('#')[0];
      var title = document.title;
      if (kind === 'copy') { window.copyText(url, 'Link copied'); return; }
      if (kind === 'native' && navigator.share) { navigator.share({ title: title, url: url }).catch(function () {}); return; }
      var map = {
        linkedin: 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url),
        x: 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(title),
        email: 'mailto:?subject=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(url)
      };
      if (map[kind]) window.open(map[kind], '_blank', 'noopener');
    });
    if (!navigator.share) { var n = document.querySelector('[data-share="native"]'); if (n) n.hidden = true; }
  }

  /* ---------- Footer year ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) { el.textContent = new Date().getFullYear(); });

  initIndex();
  initArticle();
})();
