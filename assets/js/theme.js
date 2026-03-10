/* ═══════════════════════════════════════════════════════════
   AI Systems Landscape 2026 — Theme Toggle
   ═══════════════════════════════════════════════════════════ */

(function() {
  var saved = localStorage.getItem('ai-landscape-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateToggleUI(saved);

  function updateToggleUI(t) {
    var icon = document.getElementById('themeIcon');
    var label = document.getElementById('themeLabel');
    if (icon) icon.innerHTML = t === 'dark' ? '\u263E' : '\u2604';
    if (label) label.textContent = t === 'dark' ? 'Dark' : 'Light';
  }

  window.toggleTheme = function() {
    var current = document.documentElement.getAttribute('data-theme') || 'dark';
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('ai-landscape-theme', next);
    updateToggleUI(next);

    /* Update Chart.js colors if charts exist */
    if (window.Chart) {
      Chart.helpers.each(Chart.instances, function(chart) {
        var isDark = next === 'dark';
        var gridColor = isDark ? '#2a2d38' : '#d0d7de';
        var tickColor = isDark ? '#9a9690' : '#57606a';
        var legendColor = isDark ? '#e8e4dd' : '#1c2028';
        if (chart.options.scales) {
          Object.values(chart.options.scales).forEach(function(s) {
            if (s.ticks) s.ticks.color = tickColor;
            if (s.grid) s.grid.color = gridColor;
          });
        }
        if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
          chart.options.plugins.legend.labels.color = legendColor;
        }
        chart.update('none');
      });
    }
  };
})();
