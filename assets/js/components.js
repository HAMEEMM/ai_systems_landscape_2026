/* ═══════════════════════════════════════════════════════════
   AI Systems Landscape 2026 — Shared Components JS
   ═══════════════════════════════════════════════════════════ */

/* ── Reading Progress Bar ── */
window.addEventListener('scroll', function() {
  var bar = document.querySelector('.reading-progress');
  if (!bar) return;
  var h = document.documentElement.scrollHeight - window.innerHeight;
  bar.style.width = h > 0 ? (window.scrollY / h * 100) + '%' : '0%';
  var btn = document.querySelector('.scroll-top');
  if (btn) btn.classList.toggle('visible', window.scrollY > 600);
});

/* ── Quiz Answer Check ── */
function checkAnswer(btn) {
  var q = btn.closest('.quiz-question');
  if (q.classList.contains('answered')) return;
  q.classList.add('answered');
  var correct = btn.dataset.correct === 'true';
  btn.classList.add(correct ? 'correct' : 'wrong');
  if (!correct) q.querySelector('[data-correct="true"]').classList.add('correct');
  q.querySelectorAll('.quiz-option').forEach(function(b) {
    if (b !== btn && !b.classList.contains('correct')) b.classList.add('disabled');
  });
  q.querySelector('.quiz-feedback').textContent = correct ? ' Correct!' : ' Not quite \u2014 see the highlighted answer.';
  q.querySelector('.quiz-feedback').style.color = correct ? 'var(--accent2)' : 'var(--accent5)';
}

/* ── Deep-Dive Toggle ── */
function toggleDeepDive(btn, id) {
  var el = document.getElementById(id);
  if (!el) return;
  var collapsed = el.classList.toggle('collapsed');
  btn.classList.toggle('open', !collapsed);
}
